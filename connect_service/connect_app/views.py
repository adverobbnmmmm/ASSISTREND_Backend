from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserAccount,Interest,UserInterest,InstantInterest
from rest_framework.permissions import AllowAny

from .serializers import (
    UserAccountSerializer, MatchSerializer, MatchResponseSerializer,InterestSerializer
)
from .matching import find_matches

class UserAccountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserAccount.objects.all()
    serializer_class = UserAccountSerializer
    permission_classes = [AllowAny]
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
    
    @action(detail=False, methods=['get'], url_path='interests')
    def get_interests(self, request):
        interests = Interest.objects.all()
        serializer = InterestSerializer(interests, many=True)
        return Response(serializer.data)

    # insert multiple interests for a user
    @action(detail=False, methods=['post'], url_path='add-interests')
    def add_interests(self, request):
        user_id = request.data.get('userId')
        interest_ids = request.data.get('interestIds')
        print(interest_ids ) # list of interest IDs
        if not user_id or not interest_ids or not isinstance(interest_ids, list) or len(interest_ids) == 0:
            return Response(
                {'error': 'userId and interestIds (non-empty list) are required'}, 
                status=400
            )
        try:
            user = UserAccount.objects.get(id=user_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        for interest_id in interest_ids:
            interest = Interest.objects.get(id=interest_id)
            InstantInterest.objects.get_or_create(user=user, interest=interest)
        return Response({'message': 'Interests added successfully'}) 

 