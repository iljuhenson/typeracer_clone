from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from . import models
from . import serializers



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def currentUserStatsView(request):
    if request.method == 'GET':
        current_user = request.user
        
        serializer = serializers.UserAndStatsSerializer(current_user)
        return Response(serializer.data)


