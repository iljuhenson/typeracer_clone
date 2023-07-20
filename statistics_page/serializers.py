from rest_framework import serializers
from django.contrib.auth.models import User

from race_handler.models import Race, RaceStatistics
from quotes_interface.models import Quotes

class QuoteField(serializers.RelatedField):
    def to_representation(self, value):
        return (value.quote.quote)


class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quotes
        fields = ['quote', ]


class RaceSerializer(serializers.ModelSerializer):
    quote = QuoteSerializer(read_only=True)
    
    class Meta:
        model = Race
        fields = ['quote']

class StatisticsSerializer(serializers.ModelSerializer):
    # amount_of_players = serializers.IntegerField()
    # creator = CreatorSerializer(read_only=True)
    race = RaceSerializer(read_only=True)
    class Meta:
        model = RaceStatistics
        fields = ('time_racing', 'place', 'average_speed', 'race')

class UserAndStatsSerializer(serializers.ModelSerializer):
    races_statistics = StatisticsSerializer(many=True)
    # races_statistics = serializers.SerializerMethodField()


    class Meta:
        model = User
        fields = ['username', 'races_statistics']

    # def get_races_statistics():
    #     pass
