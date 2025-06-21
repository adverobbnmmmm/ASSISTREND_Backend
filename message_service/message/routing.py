from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # For one-to-one friend chat
    re_path(r"^wss/friend/(?P<friend_id>\d+)/$", consumers.FriendChatConsumer.as_asgi()),

    # For group chat
    re_path(r"^wss/group/(?P<group_id>\d+)/$", consumers.GroupChatConsumer.as_asgi()),
]
