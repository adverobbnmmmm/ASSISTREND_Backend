# social/views.py
from rest_framework import viewsets
from .models import Connect, Friend, Engagement, Status
from .serializers import ConnectSerializer, FriendSerializer, EngagementSerializer, StatusSerializer


class ConnectViewSet(viewsets.ModelViewSet):
    queryset = Connect.objects.all()
    serializer_class = ConnectSerializer

class FriendViewSet(viewsets.ModelViewSet):
    queryset = Friend.objects.all()
    serializer_class = FriendSerializer


class EngagementViewSet(viewsets.ModelViewSet):
    queryset = Engagement.objects.all()
    serializer_class = EngagementSerializer

class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
