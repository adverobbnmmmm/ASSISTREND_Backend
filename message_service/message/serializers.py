# message/serializers.py

from rest_framework import serializers
from .models import UserAccount

class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        # Include all fields that help build user profiles
        fields = '__all__'
