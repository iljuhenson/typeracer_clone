from rest_framework import serializers

from . import models


class RaceSerializer(serializers.ModelSerializer):
    creator = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    amount_of_players = serializers.IntegerField()

    class Meta:
        model = models.Race
        fields = ('id', 'creator', 'status', 'amount_of_players')