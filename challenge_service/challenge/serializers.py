# challenge/serializers.py
from rest_framework import serializers
from .models import Challenge, ChallengeTrack, Leaderboard


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = '__all__'

class ChallengeTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallengeTrack
        fields = '__all__'

class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leaderboard
        fields = '__all__'