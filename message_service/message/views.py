# social/views.py
from rest_framework import viewsets
from .models import MessageGroup, Message1to1
from .serializers import Message1to1Serializer, MessageGroupSerializer


class MessageGroupViewSet(viewsets.ModelViewSet):
    queryset = MessageGroup.objects.all()
    serializer_class = MessageGroupSerializer

class Message1to1ViewSet(viewsets.ModelViewSet):
    queryset = Message1to1.objects.all()
    serializer_class = Message1to1Serializer
