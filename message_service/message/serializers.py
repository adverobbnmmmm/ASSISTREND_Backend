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
    class Meta:
        model = UserAccount
        fields = ["id", "username"]

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = ["id", "name"]
