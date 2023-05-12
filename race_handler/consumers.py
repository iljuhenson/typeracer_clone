import threading
import random
import time
import datetime

from django.db.models import Q
from django.core.cache import cache
from django.conf import settings

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from . import models
from quotes_interface.models import Quotes

class RaceHandlerConsumer(JsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.race_id = None
        self.race_details = None
        self.race_name = None
        self.word_index = 0
        self.is_race_started_key = None
        self.race_text_key = None
        self.race_text = None
        self.race_start_time_key = None
        self.race_end_time = None
        self.server_lifetime_time_key = None
        self.starting_time_key = None

    def connect(self):
        if not self.scope['user'].is_authenticated:
            self.close()
            return

        self.race_id = self.scope['url_route']['kwargs']['race_id']
        
        try: 
            self.race_details = models.Race.objects.get(id = self.race_id, status="w")
        except:
            self.close()
            return

        self.server_lifetime_time_key = f"{self.race_name}_server_time_left"
        if not cache.has_key(self.server_lifetime_time_key):
            threading.Thread(target=self.start_server_lifetime_timer)

        self.race_name = f"race_{self.race_id}"

        players = cache.has_key(self.race_name)

        if not players:
            players = []
        else:
            players = cache.get(self.race_name)

        if {'id' : self.scope['user'].id, 'username' : self.scope['user'].username} in players:
            self.scope['user'] = None
            self.close()
            return

        players.append({'id' : self.scope['user'].id, 'username' : self.scope['user'].username})
        cache.set(self.race_name, players, settings.REDIS_CACHE_TIMEOUT)

        self.race_text_key = f"{self.race_name}_text"
        self.starting_time_key = f"{self.race_name}_starting_time"
        self.is_race_started_key = f"{self.race_name}_status"

        is_race_started = cache.get(self.is_race_started_key)
        starting_time = cache.get(self.starting_time_key)
        async_to_sync(self.channel_layer.group_add)(self.race_name, self.channel_name)
        
        self.accept()
        
        if len(players) == 3 and not is_race_started:
            starting_time = 10.0
            cache.set(self.starting_time_key, starting_time, settings.REDIS_CACHE_TIMEOUT)
            starting = threading.Thread(target=self.start_race)
            starting.start()
        
        async_to_sync(self.channel_layer.group_send)(self.race_name, {
            'type': 'player_list',
            'players': players,
            'time' : starting_time
        })

    def disconnect(self, close_code):
        if not self.scope['user'] or not self.scope['user'].is_authenticated:
            return

        players = cache.get(self.race_name)
        players.remove({'id' : self.scope['user'].id, 'username' : self.scope['user'].username})
        cache.set(self.race_name, players, settings.REDIS_CACHE_TIMEOUT)


        is_race_started = cache.get(self.is_race_started_key)
        async_to_sync(self.channel_layer.group_discard)(self.race_name, self.channel_name)
        
        if len(players) == 0 and models.Race.objects.get(id = self.race_id).status != 'f':
            models.Race.objects.get(id = self.race_id).delete()
            self.clean_race_cache()
            return

        if len(players) == 0:
            self.clean_race_cache()
            return

        starting_time = cache.get(self.starting_time_key)

        async_to_sync(self.channel_layer.group_send)(self.race_name, {
            'type': 'player_list',
            'players': players,
            'time' : starting_time,
        })

    def receive_json(self, content, **kwargs):

        is_race_started = cache.get(self.is_race_started_key)
        try:
            content_type = content['type'] 
        except KeyError:
            self.send_json({
                    'type' : 'error',
                    'text' : 'Wrong message format',
                })
            return

        if content_type == 'race_action':
            if content['action'] == 'start_race':
                
                is_race_started = cache.get(self.is_race_started_key)

                if is_race_started == True:
                    return

                if self.scope['user'].id == self.race_details.creator.id:
                    starting_time = 5.0
                    cache.set(self.starting_time_key, starting_time, settings.REDIS_CACHE_TIMEOUT)
                    starting = threading.Thread(target=self.start_race)
                    
                    starting.start()
                    return

            self.send_json({
                    'type' : 'error',
                    'text' : 'Wrong message format',
                })
            return

        if is_race_started and content_type == 'race_progress':

            try:
                players_word = content['word']
            except KeyError:
                self.send_json({
                    'type' : 'error',
                    'text' : 'Wrong message format',
                })
                return
            
            if not self.race_text:
                self.race_text = cache.get(self.race_text_key).split()

            if not self.race_text[self.word_index] == players_word:
                self.send_json({
                    'type' : 'race_error',
                    'text' : 'Wrong word was sent. Race cannot be continued for that user until the correct word will be sent',
                })
                return
            elif self.word_index + 1 != len(self.race_text):
                self.word_index = self.word_index + 1
                async_to_sync(self.channel_layer.group_send)(self.race_name, {
                    'type': 'race_progress',
                    'user_id': self.scope['user'].id,
                    'word': players_word,
                })
                return
            elif self.word_index + 1 == len(self.race_text):
                self.word_index = self.word_index + 1
                self.race_end_time = time.perf_counter()
                race = models.Race.objects.get(id = self.race_id)
                race.participants.add(self.scope['user'])
                race.status = 'f'
                race.save()
                race.statistics.create(time_racing = datetime.timedelta(seconds=self.race_end_time - cache.get(self.race_start_time_key)), finished = True, player = self.scope['user'])
                async_to_sync(self.channel_layer.group_send)(self.race_name, {
                    'type': 'race_progress',
                    'user_id': self.scope['user'].id,
                    'word': players_word,
                })
                return


    def start_race(self):
        is_race_started = cache.get(self.is_race_started_key)

        if is_race_started:
            return

        cache.set(self.is_race_started_key, True, settings.REDIS_CACHE_TIMEOUT)
        players = cache.get(self.race_name)
        starting_time = cache.get(self.starting_time_key)

        async_to_sync(self.channel_layer.group_send)(self.race_name, {
            'type': 'player_list',
            'players': players,
            'time' : starting_time,
        })

        
        for second in range(int(starting_time)):
            time.sleep(1)
            cache.set(self.starting_time_key, starting_time - second - 1, settings.REDIS_CACHE_TIMEOUT)

        quotes_to_choose = Quotes.objects.all()

        random_quote = random.choice(list(quotes_to_choose))

        categories = quotes_to_choose.get(id = random_quote.id).categories.all()
        category_list = []
        for category in list(categories):
            category_list.append(category.category)

        race = models.Race.objects.get(id = self.race_id)
        race.status = 's'
        race.quote = random_quote
        race.save()

        cache.set(self.race_text_key, random_quote.quote, settings.REDIS_CACHE_TIMEOUT)
        cache.set(self.race_start_time_key, time.perf_counter(), settings.REDIS_CACHE_TIMEOUT)
        
        async_to_sync(self.channel_layer.group_send)(self.race_name, {
            'type' : 'race_start',
            'quote' : random_quote.quote,
            'author' : random_quote.author,
            'categories' : category_list,
        })

    
    def start_server_lifetime_timer(self):
        cache.set(self.server_lifetime_time_key, settings.REDIS_CACHE_TIMEOUT, settings.REDIS_CACHE_TIMEOUT)

        for seconds in range(int(settings.REDIS_CACHE_TIMEOUT)):
            time.sleep(1)
            if not cache.has_key(self.server_lifetime_time_key):
                return

        async_to_sync(self.channel_layer.group_send)(self.race_name, {
            'type' : 'server_close',
        })

    def clean_race_cache(self):
        cache.delete(self.race_name)
        cache.delete(self.is_race_started_key)
        cache.delete(self.race_text_key)
        cache.delete(self.race_start_time_key)
        cache.delete(self.server_lifetime_time_key)
        cache.delete(self.starting_time_key)

    def player_list(self, event):
        self.send_json(event)
    
    def race_starting_timer(self, event):
        self.send_json(event)

    def race_start(self, event):
        self.send_json(event)

    def race_progress(self, event):
        self.send_json(event)

    def server_close(self, event):
        self.close()

