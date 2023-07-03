
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q 

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from . import models
from . import serializers


@api_view(['GET'])
def race_list(request):
    """
    List all available races
    """
    if request.method == 'GET':
        races = models.Race.objects.filter(Q(status='w') | Q(status='t')).annotate(amount_of_players=Count('participants'))
        serializer = serializers.RaceSerializer(races, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_race(request):
    if request.method == 'POST':
        current_user = request.user
        race = models.Race.objects.create(creator=current_user)
        serializer = serializers.RaceSerializer(race)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def force_start_race_timer(request, race_id):
#     if request.method == 'GET':
#         current_user = request.user
#         race = get_object_or_404(models.Race, id = race_id)

#         if current_user != race.creator:
#             return Response({"error" : "You are not allowed to start a race because unless you are the creator of the race"}, status=status.HTTP_403_FORBIDDEN)
        
#         if race.status != "t":
#             return Response({"error" : "You can't start race that is already started"}, status=status.HTTP_403_FORBIDDEN)


#         race.status = "t"
#         race.save()

#         return Response({}, status=status.HTTP_204_NO_CONTENT)

    

