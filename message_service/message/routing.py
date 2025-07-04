from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^wss/notifications/$', consumers.NotificationsConsumer.as_asgi()),
]
