from rest_framework import serializers

from . import models


class RaceSerializer(serializers.ModelSerializer):
    creator = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
     )

    class Meta:
        model = models.Race
        fields = ('id', 'creator')