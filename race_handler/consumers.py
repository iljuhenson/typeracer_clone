import threading
import random
import time
import datetime


from django.db.models import Q
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from . import models
from quotes_interface.models import Quotes

class RaceHandlerConsumer(JsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.race_model = None
        self.word_index = 0
        self.requires_cleanup = True


    def connect(self):
        
        self.race_id = self.scope['url_route']['kwargs']['race_id']

        if not self.check_if_authenticated():
            self.requires_cleanup = False
            self.close()
            return
        
        self.race_model = self.get_corresponding_race_model()

        if not self.race_model:
            self.requires_cleanup = False
            self.close()
            return

        

        if self.check_if_already_participates():
            self.requires_cleanup = False
            self.close()
            return

        self.add_current_user_to_participants_list()

        race_start_date = self.get_race_start_date_or_none()

        if len(self.get_participants().all()) >= 3 and not self.is_race_started():
            race_start_date = self.calculate_date_after(10.0)
            self.set_race_start_date(race_start_date)
            self.start_race_at(race_start_date)
        
        self.share_race_organisational_info(race_start_date or None)


    def disconnect(self, close_code):
        if not self.requires_cleanup:
            return

        self.remove_current_user_from_participants_list()

        if len(self.get_participants().all()) == 0 and not self.is_race_finished():
            self.delete_race_from_db()
            return

        race_start_date = self.get_race_start_date_or_none()

        self.share_race_organisational_info(race_start_date)
    
    
    def receive_json(self, content, **kwargs):
        
        content_type = self.get_content_type_or_none(content)
        
        if content_type is None:
            self.send_error_wrong_message_format()
            return

        if content_type == 'race_action':
            if content['action'] == 'start_race':
                
                if not self.is_race_started():
                    race_start_date = self.calculate_date_after(5.0)
                    self.set_race_start_date(race_start_date)
                    self.start_race_at(race_start_date)
                
                    self.share_race_organisational_info(race_start_date)
                    
                    return

            else:
                self.send_error_wrong_message_format()
                return

        if self.is_race_available_to_join():
            return
        
        if content_type == 'race_progress':

            quote = self.get_quote_of_the_game()
            
            if not self.is_typed_word_valid(content, quote):
                self.send_error_wrong_message_format()
                return 

            self.share_current_user_race_progress()

            self.word_index += 1

            if self.did_player_finish_the_race(quote):
                self.record_finished_player_stats_to_db(quote)
                self.mark_race_as_finished_in_db()
                self.share_finished_player_stats()
    
        else:
            self.send_error_wrong_message_format()
        
    def get_current_users_statistics(self):
        return self.race_model.statistics.get(player=self.get_ws_user_info())
        

    def serialize_finished_player_stats(self):
        stats = self.get_current_users_statistics()
        print(f"time_racing: {stats.time_racing.seconds}")
        return {
            'player': self.get_ws_user_info().id,
            'time_racing': str(stats.time_racing),
            'place': stats.place,
            'average_speed': stats.average_speed,
        }

    def share_finished_player_stats(self):
        self.send_everyone(self.serialize_finished_player_stats())
    
    def delete_race_from_db(self):
        self.race_model.delete()

    def get_content_type_or_none(self, content):
        try:
            return content['type']
        except KeyEror:
            return None

    def send_error_wrong_message_format(self):
        self.send_json({
                'type' : 'error',
                'text' : 'Wrong message format',
            })

    def get_typed_word_or_none(self, content):
        try:
            return content['word']
        except KeyError:
            return None

    def get_quote_of_the_game(self):
        return self.race_model.quote.quote

    def is_word_typed_in_correct_order(self, word, quote):
        word_list = quote.split()

        if word == word_list[self.word_index]:
            return True
        else:
            return False

    def is_typed_word_valid(self, content, quote):
        word = self.get_typed_word_or_none(content)
        
        if word is None:
            return False
        
        
        if not self.is_word_typed_in_correct_order(word, quote):
            return False

        return True

    def did_player_finish_the_race(self, quote):
        if len(quote.split()) == self.word_index:
            return True
        else:
            return False
        
    def mark_race_as_finished_in_db(self):
        self.change_race_status('f')

    def get_racing_time_in_seconds(self):
        finish_date = timezone.now()
        starting_date = self.race_model.start_date
        print(f"get_racing_time_in_seconds: {(finish_date - starting_date).total_seconds()}")
        return (finish_date - starting_date).total_seconds()

    def get_race_statistics_list(self):
        return self.race_model.statistics.all()

    def get_current_users_place(self):
        return len(self.get_race_statistics_list()) + 1

    def calculate_average_speed(self, racing_time, quote):
        quote_length = len(quote)
        return quote_length / racing_time

    def record_finished_player_stats_to_db(self, quote):
        racing_time_in_seconds = self.get_racing_time_in_seconds()
        
        models.RaceStatistics.objects.create(
            time_racing = datetime.timedelta(milliseconds=(racing_time_in_seconds*1000)),
            finished = True,
            player=self.get_ws_user_info(),
            race=self.race_model,
            place=self.get_current_users_place(),
            average_speed=self.calculate_average_speed(racing_time_in_seconds, quote),
        )        

    def share_current_user_race_progress(self):
        self.send_everyone({
                'type': 'race_progress',
                'player_id': self.get_ws_user_info().id,
                'word_index': self.word_index,
            })

    def calculate_time_before_start_in_seconds(self, start_date):
        return (start_date - timezone.now()).total_seconds()

    def change_race_status(self, status):
        self.race_model.status = status
        self.race_model.save()

    def change_race_status_to_on_timer(self):
        self.race

    def start_race_at(self, start_date):
        if self.is_race_started():
            return

        self.change_race_status("t")

        time_before_start_in_seconds = self.calculate_time_before_start_in_seconds(start_date)

        starting = threading.Thread(target=self.start_race, kwargs={'time_before_start' : time_before_start_in_seconds})
        starting.start()
        

    def wait(self, waiting_time):
        time.sleep(waiting_time)

    def get_quotes_categories(self, quote):
        categories = Quotes.objects.get(id = quote.id).categories.all()
        
        category_list = []
        for category in list(categories):
            category_list.append(category.category)

        return category_list


    def get_random_quote(self):
        quotes_to_choose = Quotes.objects.all()

        return random.choice(list(quotes_to_choose))



    def record_race_start_info_to_db(self, quote, status):
        self.race_model.status = status
        self.race_model.quote = quote
        self.race_model.save()

    def share_race_start_info(self, quote, categories):
        self.send_everyone({
            'type' : 'race_start',
            'quote' : quote.quote,
            'author' : quote.author,
            'categories' : categories,
        })


    def start_race(self, time_before_start):
        self.wait(time_before_start)
        
        quote = self.get_random_quote()
        categories = self.get_quotes_categories(quote)
        
        self.record_race_start_info_to_db(quote, "s")

        self.share_race_start_info(quote, categories)
        
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

    def send_everyone(self, dict_to_send):
        async_to_sync(self.channel_layer.group_send)(self.race_id, dict_to_send)
        
    def check_if_authenticated(self):
        if not self.get_ws_user_info().is_authenticated:
            return False
        else:
            return True

    def get_corresponding_race_model(self):
        race_id = self.scope['url_route']['kwargs']['race_id']

        try: 
            return models.Race.objects.get(Q(id = race_id), (Q(status="w") | Q(status="t")))
        except:
            return None

    def get_ws_user_info(self):
        return self.scope['user']

    def add_current_user_to_participants_list(self):
        self.get_participants().add(get_user_model().objects.get(id=self.get_ws_user_info().id))
        self.race_model.save()
        async_to_sync(self.channel_layer.group_add)(self.race_id, self.channel_name)
        self.accept()

    def remove_current_user_from_participants_list(self):
        self.get_participants().remove(get_user_model().objects.get(id=self.get_ws_user_info().id))
        self.race_model.save()
        
        async_to_sync(self.channel_layer.group_discard)(self.race_id, self.channel_name)

    def get_participants(self):
        return self.race_model.participants
        
    def check_if_already_participates(self):
        if self.get_participants().filter(id=self.get_ws_user_info().id).exists():
            return True
        else:
            return False

    def calculate_date_after(self, seconds):
        return timezone.now() + datetime.timedelta(seconds=seconds)

    def is_race_started(self):
        if self.race_model.status == "w":
            return False
        else:
            return True

    def is_race_available_to_join(self):
        if self.race_model.status == "w" or self.race_model.status == "t":
            return True
        else:
            return False

    def is_race_finished(self):
        if self.race_model.status == "f":
            return True
        else:
            return False

    def set_race_start_date(self, start_date):
        self.race_model.start_date = start_date
        self.race_model.save()

    def get_race_start_date_or_none(self):
        return self.race_model.start_date
        
    def serialize_participants(self):
        participants_qs = self.get_participants().all()

        participant_list = []

        for participant_qs in participants_qs:
            participant_list.append({'id':participant_qs.id, 'username':participant_qs.username,})

        return participant_list

    def share_race_organisational_info(self, start_date):

        game_info = {
            'type': 'player_list',
            'players': self.serialize_participants(),
        }

        if start_date is not None:
            game_info['time'] = start_date.isoformat()

        self.send_everyone(game_info)
