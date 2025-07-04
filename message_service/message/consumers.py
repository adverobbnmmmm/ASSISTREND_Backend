# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import Q
from .models import (
    OneToOneMessage,
    GroupMessage,
    ChatGroup,
    UserAccount,
    Friendship
)

# =======================================
# NotificationsConsumer
# =======================================
# This single consumer handles:
# - Receiving messages
# - Storing them in DB
# - Sending notifications to recipients
# - Handling acknowledgements
#
# One connection per user.
#
class NotificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Called when WebSocket connection is established.
        """
        self.user = self.scope["user"]
        self.room_group_name = f"user_notifications_{self.user.id}"

        # Add this connection to Redis group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept connection
        await self.accept()

        # Optional: confirm connection to client
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "Notifications WebSocket connected successfully."
        }))

    async def disconnect(self, close_code):
        """
        Called when WebSocket connection closes.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Handles incoming data from client.
        """
        data = json.loads(text_data)

        if data["type"] == "chat_message":
            # Incoming chat message
            chat_type = data["chat_type"]
            target_id = data["target_id"]
            message = data.get("message", "")
            image = data.get("image", None)

            if chat_type == "friend":
                # Save and notify friend
                await self.handle_friend_message(target_id, message, image)
            elif chat_type == "group":
                # Save and notify group
                await self.handle_group_message(target_id, message, image)

        elif data["type"] == "acknowledge":
            # Acknowledgment of delivery
            chat_type = data["chat_type"]
            message_id = data["message_id"]

            if chat_type == "friend":
                await self.acknowledge_friend_message(message_id)
            elif chat_type == "group":
                await self.acknowledge_group_message(message_id)

        else:
            # Unknown message type
            await self.send(text_data=json.dumps({
                "error": "Invalid message type."
            }))

    # =======================
    # Friend Message Handling
    # =======================
    async def handle_friend_message(self, friend_id, message, image):
        """
        Saves a one-to-one message and notifies recipient.
        """
        is_friend = await self.check_friendship(friend_id)
        if not is_friend:
            await self.send(text_data=json.dumps({
                "error": "You are not friends with this user."
            }))
            return

        msg_id = await self.save_friend_message(friend_id, message, image)

        # Send notification to recipient
        await self.channel_layer.group_send(
            f"user_notifications_{friend_id}",
            {
                "type": "notify",
                "event_type": "new_one_to_one_message",
                "payload": {
                    "id": msg_id,
                    "sender_id": self.user.id,
                    "message": message,
                    "image": image,
                }
            }
        )

    @database_sync_to_async
    def check_friendship(self, friend_id):
        """
        Checks if the current user and friend_id are friends.
        """
        return Friendship.objects.filter(
            Q(user1=self.user, user2_id=friend_id) |
            Q(user1_id=friend_id, user2=self.user)
        ).exists()

    @database_sync_to_async
    def save_friend_message(self, friend_id, message, image):
        """
        Saves OneToOneMessage to DB.
        """
        friend = UserAccount.objects.get(id=friend_id)
        msg = OneToOneMessage.objects.create(
            sender=self.user,
            receiver=friend,
            message=message,
            image=image
        )
        return msg.id

    @database_sync_to_async
    def acknowledge_friend_message(self, message_id):
        """
        Marks OneToOneMessage as delivered.
        """
        try:
            msg = OneToOneMessage.objects.get(id=message_id, receiver=self.user)
            msg.sent_to_receiver = True
            msg.save()
        except OneToOneMessage.DoesNotExist:
            pass

    # =======================
    # Group Message Handling
    # =======================
    async def handle_group_message(self, group_id, message, image):
        """
        Saves a group message and notifies group members.
        """
        msg_id = await self.save_group_message(group_id, message, image)
        group_members = await self.get_group_member_ids(group_id)

        # Send notifications to all members except sender
        for member_id in group_members:
            if member_id != self.user.id:
                await self.channel_layer.group_send(
                    f"user_notifications_{member_id}",
                    {
                        "type": "notify",
                        "event_type": "new_group_message",
                        "payload": {
                            "id": msg_id,
                            "group_id": group_id,
                            "sender_id": self.user.id,
                            "message": message,
                            "image": image,
                        }
                    }
                )

    @database_sync_to_async
    def save_group_message(self, group_id, message, image):
        """
        Saves GroupMessage to DB.
        """
        group = ChatGroup.objects.get(id=group_id)
        msg = GroupMessage.objects.create(
            sender=self.user,
            group=group,
            message=message,
            image=image
        )
        return msg.id

    @database_sync_to_async
    def get_group_member_ids(self, group_id):
        """
        Returns list of user IDs in the group.
        """
        return list(
            ChatGroup.objects.get(id=group_id).members.values_list("id", flat=True)
        )

    @database_sync_to_async
    def acknowledge_group_message(self, message_id):
        """
        Marks GroupMessage as delivered to this user.
        """
        try:
            msg = GroupMessage.objects.get(id=message_id)
            msg.delivered_to.add(self.user)
        except GroupMessage.DoesNotExist:
            pass

    # =======================
    # Notifier
    # =======================
    async def notify(self, event):
        """
        Called automatically when group_send is triggered for this user's notifications group.
        Pushes data to WebSocket.
        """
        await self.send(text_data=json.dumps({
            "type": event["event_type"],
            "payload": event["payload"]
        }))
