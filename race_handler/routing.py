from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/race/(?P<race_id>\w+)/$", consumers.RaceHandlerConsumer.as_asgi()),
]           