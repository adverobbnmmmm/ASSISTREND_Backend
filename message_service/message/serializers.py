# social/serializers.py
from rest_framework import serializers
from .models import Message1to1, MessageGroup


class Message1to1Serializer(serializers.ModelSerializer):
    class Meta:
        model = Message1to1
        fields = '__all__'

class MessageGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageGroup
        fields = '__all__'