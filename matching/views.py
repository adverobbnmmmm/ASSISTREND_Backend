from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import UserProfile,User
from .serializers import UserProfileSerializer, MatchSerializer, MatchResponseSerializer
from .matching import find_matches

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):/
    
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def matches(self, request):
        matches = find_matches(request.user)

        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def respond_to_match(self, request):
        serializer = MatchResponseSerializer(data=request.data)
        if serializer.is_valid():
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def online_users(self, request):
        return Response([])
