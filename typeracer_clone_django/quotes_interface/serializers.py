from rest_framework import serializers


class QuoteSerializer(serializers.Serializer):
    quote = serializers.CharField()
    author = serializers.CharField()
    category = serializers.ListField(
        child=serializers.CharField()
    )