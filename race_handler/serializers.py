from rest_framework import serializers
from django.contrib.auth.models import User

from . import models


class CreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class RaceSerializer(serializers.ModelSerializer):
    amount_of_players = serializers.IntegerField()
    creator = CreatorSerializer(read_only=True)

    class Meta:
        model = models.Race
        fields = ('id', 'creator',  'status', 'amount_of_players')