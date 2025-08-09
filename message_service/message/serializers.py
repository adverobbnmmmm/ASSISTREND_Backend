# message/serializers.py

from rest_framework import serializers
from .models import UserAccount
from .models import ChatGroup, UserAccount


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        # Include all fields that help build user profiles
        fields = '__all__'

class FriendSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = UserAccount
        fields = ["id", "name", "profile_picture"]

    def get_profile_picture(self, obj):
        if obj.profilepicture:
            return obj.profilepicture.url
        return ""

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = ["id", "group_name"]
