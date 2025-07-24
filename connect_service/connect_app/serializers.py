from rest_framework import serializers
from .models import UserAccount, Interest, UserInterest

class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'interestName']

class UserAccountSerializer(serializers.ModelSerializer):
    interests = serializers.SerializerMethodField()
    class Meta:
        model = UserAccount
        fields = ['id', 'name', 'email', 'location', 'gender', 'bio', 'dob', 'interests','profilepicture']
    def get_interests(self, obj):
        return [i.interestName for i in Interest.objects.filter(userinterest__userId=obj)]

class MatchSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    name = serializers.CharField()
    profilepicture=serializers.ImageField()
    phone=serializers.CharField()
    score = serializers.IntegerField()
    hobbies = serializers.ListField(
        child=serializers.CharField(), required=False
    )

class MatchResponseSerializer(serializers.Serializer):
    match_id = serializers.IntegerField()
    response = serializers.ChoiceField(choices=['accept', 'decline'])
