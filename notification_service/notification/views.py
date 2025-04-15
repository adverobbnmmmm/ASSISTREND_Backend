# notifications/views.py
from rest_framework import viewsets, mixins
from .models import Notification
from .serializers import NotificationSerializer

class NoDeletionViewSet(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    pass

class NotificationViewSet(NoDeletionViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
