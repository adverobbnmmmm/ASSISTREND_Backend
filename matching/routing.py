from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/status/', consumers.StatusConsumer.as_asgi()),
]
