from rest_framework import serializers
from .models import UserAccount, Interest

class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'interestName']


class UserAccountSerializer(serializers.ModelSerializer):
    interests = serializers.SerializerMethodField()

    class Meta:
        model = UserAccount
        fields = ['id', 'name', 'email', 'location', 'gender', 'bio', 'dob', 'interests', 'profilepicture']

    def get_interests(self, obj):
        return list(
            Interest.objects.filter(userinterests__userId=obj)
            .values_list('interestName', flat=True)
        )


class MatchSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    name = serializers.CharField()
    profilepicture = serializers.ImageField()
    phone = serializers.CharField()
    score = serializers.IntegerField()
    interests = serializers.ListField(child=serializers.CharField(), required=False)


class MatchResponseSerializer(serializers.Serializer):
    match_id = serializers.IntegerField()
    response = serializers.ChoiceField(choices=['accept', 'decline'])
