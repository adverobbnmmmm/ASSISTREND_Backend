# challenge/views.py
from rest_framework import viewsets
from .models import Challenge, ChallengeTrack, Leaderboard
from .serializers import ChallengeSerializer, ChallengeTrackSerializer, LeaderboardSerializer


class ChallengeViewSet(viewsets.ModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer

class ChallengeTrackViewSet(viewsets.ModelViewSet):
    queryset = ChallengeTrack.objects.all()
    serializer_class = ChallengeTrackSerializer

class LeaderboardViewSet(viewsets.ModelViewSet):
    queryset = Leaderboard.objects.all()
    serializer_class = LeaderboardSerializer
