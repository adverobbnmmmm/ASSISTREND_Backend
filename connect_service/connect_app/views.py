from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserAccount
from rest_framework.permissions import AllowAny
from .serializers import (
    UserAccountSerializer, MatchSerializer, MatchResponseSerializer
)
from .matching import find_matches

class UserAccountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserAccount.objects.all()
    serializer_class = UserAccountSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['GET'])
    def matches(self, request):
        user = request.user
        matches = find_matches(user)
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def respond_to_match(self, request):
        serializer = MatchResponseSerializer(data=request.data)
        if serializer.is_valid():
            # Save the response in the db if required
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['get'], url_path='get_online_users')
    def get_online_users(self, request):
        # logic to return online users
        users = UserAccount.objects.filter(is_active=True)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)