import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

class StatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.username = self.user.username

        await self.channel_layer.group_add(f"user_{self.username}", self.channel_name)
        await self.accept()
        await self.change_online_status(self.username, "open")

    async def disconnect(self, close_code):
        await self.change_online_status(self.username, "close")
        await self.channel_layer.group_discard(f"user_{self.username}", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type", "")

        if message_type == "status_check":
            target_user = data.get("user")
            status = await self.get_user_status(target_user)
            await self.send(json.dumps({"type": "status_update", "user": target_user, "status": status}))
        elif message_type == "call_offer":
            await self.channel_layer.group_send(
                f"user_{data.get('target')}",
                {"type": "call_signal", "signal_type": "offer", "from_user": self.username, "offer": data.get("offer")}
            )
        elif message_type == "call_answer":
            await self.channel_layer.group_send(
                f"user_{data.get('target')}",
                {"type": "call_signal", "signal_type": "answer", "from_user": self.username, "answer": data.get("answer")}
            )

    @database_sync_to_async
    def change_online_status(self, username, c_type):
        from .models import UserProfile
        try:
            user = User.objects.get(username=username)
            profile = UserProfile.objects.get(user=user)
            profile.online_status = (c_type == "open")
            profile.save()
        except User.DoesNotExist:
            pass

    @database_sync_to_async
    def get_user_status(self, username):
        from .models import UserProfile
        try:
            user = User.objects.get(username=username)
            return UserProfile.objects.get(user=user).online_status
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            return False

    async def call_signal(self, event):
        await self.send(text_data=json.dumps(event))
