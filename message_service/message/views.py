# social/views.py

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache #for storig session token
from .models import FriendRequest, Friendship, OneToOneMessage,GroupMessage,ChatGroup, UserAccount
from django.db.models import Q
import secrets
import datetime

class RequestSocketSession(APIView):#API end-point for requesting a socket session.
    permission_classes = [IsAuthenticated] #Ensures JWT is validated
    
    def post(self,request):
        user = request.user # this now is the authenticated user.
        chat_type = request.data.get('chat_type')
        socket_session_token = secrets.token_urlsafe(32)# session token for url and user session authentication in socket connection.
        cache.set(f"ws_session_{socket_session_token}",user.id,timeout=300)
        #session token stored in cache expires after 5 mins, session can be made within 5 mins
        target_id = request.data.get('target_id') #backend gets the which friend or group it refers to.
        
        if(chat_type=='friend'):
            websocket_url = f"wss://127.0.0.1:8001/wss/friend/{target_id}?token={socket_session_token}"
        if(chat_type=='group'):
            websocket_url = f"wss://127.0.0.1:8001/wss/group/{target_id}?token={socket_session_token}"

        #return the session info to the client
        return Response({
            "websocket_url": websocket_url,
            "socket_session_token":socket_session_token,
            "expires_in_seconds":300,
            "message":("Use this url for opening a websocket connection")
        })
    

class GetMissedChats(APIView):#API endpoint for getting the chats sent to the user while they were offline
    """
    API endpoint to fetch all missed messages (one-to-one and group) 
    that were sent while the user was offline, and update the DB as acknowledged.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):  # GET is more appropriate than POST here
        user = request.user

        # =====================
        # 1. One-to-One Messages
        # =====================
        one_to_one_msgs = OneToOneMessage.objects.filter(
            receiver=user,
            sent_to_receiver=False
        )

        # Collect them for response
        one_to_one_payload = [{
            "id": msg.id,
            "sender_id": msg.sender.id,
            "message": msg.message,
            "image": msg.image.url if msg.image else None,
            "timestamp": msg.timestamp
        } for msg in one_to_one_msgs]

        # Mark these messages as delivered
        one_to_one_msgs.update(sent_to_receiver=True)


        # =====================
        # 2. Group Messages
        # =====================
        # Get all groups this user belongs to
        user_groups = ChatGroup.objects.filter(members=user)

        # Find group messages the user hasn't acknowledged
        group_msgs = GroupMessage.objects.filter(
            group__in=user_groups
        ).exclude(
            delivered_to=user
        )

        # Prepare response payload
        group_payload = [{
            "id": msg.id,
            "group_id": msg.group.id,
            "sender_id": msg.sender.id,
            "message": msg.message,
            "image": msg.image.url if msg.image else None,
            "timestamp": msg.timestamp
        } for msg in group_msgs]

        # Mark them as delivered to this user
        for msg in group_msgs:
            msg.delivered_to.add(user)

        # =====================
        # Return All Missed Messages
        # =====================
        return Response({
            "one_to_one_messages": one_to_one_payload,
            "group_messages": group_payload
        })


# ================================
# Send a Friend Request View
# ================================
class SendFriendRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        receiver_id = request.data.get('receiver_id')  # ID of user being sent request
        message = request.data.get('message', '')      # Optional message to include

        if receiver_id == request.user.id:
            return Response({"error": "You cannot send a friend request to yourself."}, status=400)

        receiver = get_object_or_404(UserAccount, id=receiver_id)

        # Prevent duplicate requests
        if FriendRequest.objects.filter(sender=request.user, receiver=receiver).exists():
            return Response({"error": "Friend request already sent."}, status=400)

        # Create the friend request
        FriendRequest.objects.create(sender=request.user, receiver=receiver, message=message)

        return Response({"message": "Friend request sent successfully."}, status=201)


# ==================================
# Accept or Reject a Friend Request
# ==================================
class RespondToFriendRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request_id = request.data.get('request_id')
        action = request.data.get('action')  # 'accept' or 'reject'

        friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)

        if action == 'accept':
            # Create the friendship
            user1, user2 = sorted([friend_request.sender, friend_request.receiver], key=lambda u: u.id)
            Friendship.objects.get_or_create(user1=user1, user2=user2)
            friend_request.is_accepted = True
            friend_request.save()
            return Response({"message": "Friend request accepted."}, status=200)

        elif action == 'reject':
            friend_request.is_rejected = True
            friend_request.save()
            return Response({"message": "Friend request rejected."}, status=200)

        else:
            return Response({"error": "Invalid action."}, status=400)


# ========================================
# View Pending Friend Requests for a User
# ========================================
class PendingFriendRequests(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all incoming friend requests that are not yet accepted/rejected
        pending = FriendRequest.objects.filter(receiver=request.user, is_accepted=False, is_rejected=False)
        data = [
            {
                'id': fr.id,
                'from': fr.sender.name,
                'sender_id': fr.sender.id,
                'message': fr.message,
                'timestamp': fr.timestamp
            }
            for fr in pending
        ]
        return Response(data, status=200)
