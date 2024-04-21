import json
import asyncio
import datetime

from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITransactionTestCase
from rest_framework_simplejwt.tokens import RefreshToken
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from channels.db import database_sync_to_async

from . import models
from quotes_interface.models import Quotes, Categories
from .routing import websocket_urlpatterns
from config.channels_middleware import JwtAuthMiddlewareStack
from time import perf_counter

ADDITIONAL_USERS = [
    {
        'username':'AdditionalTestUser1',
        'password':'TestPass.123',
        'email':'additionaluser1@tester.com',
        'first_name':'John',
        'last_name':'Smith'
    },
    {
        'username':'AdditionalTestUser2',
        'password':'TestPass.123',
        'email':'additionaluser2@tester.com',
        'first_name':'John',
        'last_name':'Smith'
    },
    {
        'username':'AdditionalTestUser3',
        'password':'TestPass.123',
        'email':'additionaluser3@tester.com',
        'first_name':'John',
        'last_name':'Smith'
    },
]

async def get_last_message(communicator):
    last_user_message = None
    
    while not await communicator.receive_nothing():
        last_user_message = await communicator.receive_json_from()

    return last_user_message

async def get_message_by_type(communicator, message_type):
    while not await communicator.receive_nothing():
        message = await communicator.receive_json_from()

        if message['type'] == message_type:
            return message

    raise ValueError(f'There is no such message type: {message_type}')

class RaceHandlerTestCase(APITransactionTestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='TestUser1',
            password='TestPass.123',
            email='testuser@tester.com',
            first_name='John',
            last_name='Smith'
        )
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = self.refresh_token.access_token

        self.headers = {'Authorization': f"Bearer {str(self.access_token)}"}
        self.url_patterns = JwtAuthMiddlewareStack(URLRouter(websocket_urlpatterns))

        self.testing_quote = Quotes.objects.create(quote = "Testing quote!", author = "Tester")
        category_names = ["Fun", "Application-making"]
        for category_name in category_names:
            category = Categories.objects.create(category=category_name)
            self.testing_quote.categories.add(category)
            self.testing_quote.save()
            

    def test_create_race(self):
        response = self.client.post('/api/races/race/create/', {}, headers=self.headers)
        print(response.json())
        self.assertEqual(response.status_code, 201)


    def test_create_race_unauthorized(self):
        response = self.client.post('/api/races/race/create/', {})
        self.assertEqual(response.status_code, 401)


    async def test_user_leaving_before_race_start(self):
        race = await database_sync_to_async(models.Race.objects.create)(creator=self.user)

        communicator = WebsocketCommunicator(self.url_patterns, f"/ws/race/{race.id}/?token={self.access_token}")
        connected, _ = await communicator.connect()

        await communicator.disconnect()

        race_in_the_end = await database_sync_to_async(models.Race.objects.filter)(id=race.id)
        race_existence = await database_sync_to_async(race_in_the_end.exists)()


        self.assertTrue(not race_existence)


    async def test_unauthenticated_user_race_access(self):
        race = await database_sync_to_async(models.Race.objects.create)(creator=self.user)
        communicator = WebsocketCommunicator(self.url_patterns, f"/ws/race/{race.id}/?token=WrongToken")
        connected, subprotocol = await communicator.connect()
        self.assertEqual(connected, False)
        
        await communicator.disconnect()


    async def test_same_user_joining_twice(self):
        race = await sync_to_async(models.Race.objects.create)(creator=self.user)

        communicator1 = WebsocketCommunicator(self.url_patterns, f"/ws/race/{race.id}/?token={self.access_token}")
        connected1, _ = await communicator1.connect()

        self.assertTrue(connected1)

        communicator2 = WebsocketCommunicator(self.url_patterns, f"/ws/race/{race.id}/?token={self.access_token}")
        connected2, _ = await communicator2.connect()

        self.assertTrue(not connected2)

        message = await get_last_message(communicator1)
        self.assertEqual(len(message['players']), 1)

        await communicator1.disconnect()
        await communicator2.disconnect()

    # For some reason this test doesn't work, but everything it checks works in real time application
    # (might be because I'm using separate thread in my consumer to countdown the time)
    async def test_solo_queue_race(self):
        race = await sync_to_async(models.Race.objects.create)(creator=self.user)

        communicator = WebsocketCommunicator(self.url_patterns, f"/ws/race/{race.id}/?token={self.access_token}")
        connected, _ = await communicator.connect()

        self.assertEqual(connected, True)

        response = await communicator.receive_json_from()

        self.assertEqual(response['type'], "player_list")
        self.assertEqual(len(response['players']), 1)

        current_time = timezone.now()
        await communicator.send_json_to({'type': 'race_action', 'action' : 'start_race'})
        time_after_start = perf_counter()
        race_start_timer_response = await communicator.receive_json_from()
        
        self.assertEqual(race_start_timer_response['type'], 'player_list')

        race_starting_time = datetime.datetime.fromisoformat(race_start_timer_response['time'])
        self.assertEqual(round((race_starting_time - current_time).total_seconds()), 5)
        
        race_start_response = await communicator.receive_json_from(timeout=7)
        
        self.assertEqual(race_start_response['type'], 'race_start')
        time_on_start = perf_counter()
        quote = race_start_response['quote']
        self.assertEqual(quote, self.testing_quote.quote)

        word_idx = 0
        for word in quote.split():
            await asyncio.sleep(0.5)
            await communicator.send_json_to({'type' : 'race_progress', 'word' : word})
            word_sent_response = await communicator.receive_json_from()

            self.assertEqual(word_sent_response, {
                'type': 'race_progress',
                'player_id': self.user.id,
                'word_index': word_idx,
            })

            word_idx += 1
            print(word)

        await communicator.disconnect()
        await sync_to_async(race.refresh_from_db)()

        race_in_the_end = await sync_to_async(models.Race.objects.get)(id=race.id)

        await sync_to_async(race_in_the_end.refresh_from_db)()
        statistics = await sync_to_async(race_in_the_end.statistics.all)()
        stat_list = await sync_to_async(list)(statistics)

        print(stat_list[0].time_racing)

        await sync_to_async(self.assertTrue)(statistics[0].time_racing > datetime.timedelta(seconds=1))

        race_status = race_in_the_end.status
        self.assertEqual(race_status, 'f')

        participants = await sync_to_async(race_in_the_end.participants.all)()
        participant_list = await sync_to_async(list)(participants)

        self.assertEqual(len(stat_list), 1)
        ws_user_id = stat_list[0].player_id
        self.assertEqual(ws_user_id, self.user.id)


    # needs some tweaks #
    async def test_multiplayer_game_playability(self):
        race = await sync_to_async(models.Race.objects.create)(creator=self.user)
        
        communicator = WebsocketCommunicator(self.url_patterns, f"/ws/race/{race.id}/?token={self.access_token}")
        connected, _ = await communicator.connect()
        
        datetime_before_last_player_joins = None

        user_list = []
        

        for user in ADDITIONAL_USERS:
            print('inside additional user loop')
            temp = await database_sync_to_async(User.objects.create)(
                username=user['username'],
                password=user['password'],
                email=user['email'],
                first_name=user['first_name'],
                last_name=user['last_name']
            )
            print('additional user created')
            refresh_token = await sync_to_async(RefreshToken.for_user)(temp)
            access_token = refresh_token.access_token

            communicator_temp = WebsocketCommunicator(self.url_patterns, f"/ws/race/{race.id}/?token={access_token}")

            datetime_before_last_player_joins = timezone.now()
            connected_temp, _ = await communicator_temp.connect()


            print(f"{user['username']} : {connected_temp}")
            self.assertTrue(connected_temp)

            user_list.append({
                'user_model':temp,
                'communicator':communicator_temp,
                'refresh_token':refresh_token,
                'access_token':access_token,
            })

            await asyncio.sleep(1)


        player_list_response = await get_last_message(user_list[0]['communicator'])

        self.assertEqual(len(player_list_response['players']), 4)

        player_list_response2 = await get_last_message(user_list[2]['communicator'])
        
        
        race_starting_datetime = datetime.datetime.fromisoformat(player_list_response2['time'])
        self.assertEqual((race_starting_datetime - datetime_before_last_player_joins).seconds, 8)


        race_start_response = await user_list[0]['communicator'].receive_json_from(timeout=11)

        self.assertEqual(race_start_response['type'], 'race_start')

        quote = race_start_response['quote']
        self.assertEqual(quote, self.testing_quote.quote)

        await user_list[0]['communicator'].disconnect()

        for word in quote.split():
            await asyncio.sleep(0.5)
            await user_list[1]['communicator'].send_json_to({'type' : 'race_progress', 'word' : word})
            word_sent_response1 = await get_last_message(user_list[1]['communicator'])
            await user_list[2]['communicator'].send_json_to({'type' : 'race_progress', 'word' : word})
            word_sent_response2 = await get_last_message(user_list[2]['communicator'])
            print(word_sent_response1)
            print(word_sent_response2)
            self.assertEqual(word_sent_response1, word_sent_response2)
            
        await communicator.disconnect()

        message_after_quit1 = await get_last_message(user_list[1]['communicator'])
        message_after_quit2 = await get_last_message(user_list[2]['communicator'])

        self.assertEqual(message_after_quit1, message_after_quit2)

        race_in_the_end = await sync_to_async(models.Race.objects.get)(id=race.id)

        statistics = await sync_to_async(race_in_the_end.statistics.all)()
        stat_list = await sync_to_async(list)(statistics)

        participants = await sync_to_async(race_in_the_end.participants.all)()
        participant_list = await sync_to_async(list)(participants)
        
        self.assertEqual(len(participants), 2)
        self.assertEqual(len(stat_list), 2)

        await user_list[1]['communicator'].disconnect()
        await user_list[2]['communicator'].disconnect()


        
