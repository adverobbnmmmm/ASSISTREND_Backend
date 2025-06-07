from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'online_status', 'last_activity', 'interests', 'preferences']

class MatchSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    score = serializers.IntegerField()
    online = serializers.BooleanField()

class MatchResponseSerializer(serializers.Serializer):
    match_id = serializers.IntegerField()
    response = serializers.ChoiceField(choices=['accept', 'decline'])
