import json
from django.db.models import Q
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Friendship, OneToOneMessage, GroupMessage, ChatGroup, UserAccount

# =====================
# Friend Chat Consumer 
# =====================
# =====================
# Friend Chat Consumer 
# =====================
class FriendChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.friend_id = self.scope["url_route"]["kwargs"]["friend_id"]
        # room_name created like this because the receiver can connect to the same group.
        self.room_name = f"private_chat_{min(self.user.id, self.friend_id)}_{max(self.user.id, self.friend_id)}"
        self.room_group_name = f"friend_{self.room_name}"

        # adding group to redis.
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        # Handle acknowledgements
        if data.get('type') == 'acknowledge':
            await self.handle_acknowledgement(data['message_id'])
            return

        # Before sending a message, ensure users are friends
        is_friend = await self.check_friendship()
        if not is_friend:
            await self.send(text_data=json.dumps({
                'error': 'You are not friends with this user. Message not sent.'
            }))
            return
        
        message = data.get('message', '')
        image_url = data.get('image', None)  # base64 or direct image URL

        # Save the message to DB
        message_id = await self.save_message(message, image_url)

        # Send it to the other user
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',
                'message': message,
                'image': image_url,
                'sender_id': self.user.id,
                'message_id': message_id
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'image': event.get('image'),  # Include image data in the response
            'sender_id': event['sender_id'],
            'message_id': event['message_id']
        }))

    @database_sync_to_async
    def save_message(self, message, image_url):
        friend = UserAccount.objects.get(id=self.friend_id)
        # Store the message with optional image
        message_object = OneToOneMessage.objects.create(
            sender=self.user,
            receiver=friend,
            message=message,
            image=image_url  # model's `image` field will accept image URL
        )
        return message_object.id

    @database_sync_to_async
    def handle_acknowledgement(self, message_id):
        try:
            msg = OneToOneMessage.objects.get(id=message_id, receiver=self.user)
            msg.sent_to_receiver = True
            msg.save()
        except OneToOneMessage.DoesNotExist:
            pass

    @database_sync_to_async
    def check_friendship(self):
        """
        Checks if a Friendship exists between self.user and self.friend_id
        in either direction (user1-user2 or user2-user1).
        """
        return Friendship.objects.filter(
            Q(user1=self.user, user2_id=self.friend_id) |
            Q(user1_id=self.friend_id, user2=self.user)
        ).exists()


# ========================
# Group Chat WebSocket Consumer
# ========================
# Handles real-time messaging within a group chat.
# Uses Redis via Django Channels for broadcasting messages to all online group members.
class GroupChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        """
        Called when a user establishes a WebSocket connection.
        We extract the group ID from the URL and add the socket to the Redis group.
        """
        self.user = self.scope["user"]  # Set by our custom middleware
        self.group_id = self.scope["url_route"]["kwargs"]["group_id"]
        self.room_group_name = f"group_chat_{self.group_id}"  # Unique room name for Redis pub-sub group

        # Add this connection to the Redis group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Called whenever a message is received from the WebSocket.
        Parses the data, saves it to the database, and broadcasts it to the group.
        """
        data = json.loads(text_data)

        #handle acknowledgement for a message
        if data.get("type") == 'acknowledge':
            await self.handle_acknowledgement(data['message_id'])
            return
        
        message = data.get('message', '')
        image_url = data.get('image', None)  # Optional image (URL or base64)

        # Save the message to the database
        message_id = await self.save_message(message, image_url)

        # Broadcast message to the Redis group so all members get it
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'group.message',  # Handler to call: group_message()
                'message': message,
                'image': image_url,
                'sender_id': self.user.id,
                'message_id':message_id
            }
        )

    async def group_message(self, event):
        """
        This gets called when the group_send message is received.
        It sends the message back to the WebSocket client.
        """
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'image': event.get('image'),
            'sender_id': event['sender_id'],
            'message_id': event['message_id']
        }))


    @database_sync_to_async
    def save_message(self, message, image_url):
        """
        Save the group message in the database, including the sender, group, message text, and image.
        Also mark it as delivered to the sender (optional delivery tracking).
        """
        group = ChatGroup.objects.get(id=self.group_id)
        
        # Save the message
        msg = GroupMessage.objects.create(
            sender=self.user,
            group=group,
            message=message,
            image=image_url  # Can be a URL or empty
        )
        return msg.id
    
    @database_sync_to_async
    def handle_acknowledgement(self,message_id):
        try:
            msg = GroupMessage.objects.get(id=message_id)
            msg.delivered_to.add(self.user)
        except GroupMessage.DoesNotExist:
            pass
    
