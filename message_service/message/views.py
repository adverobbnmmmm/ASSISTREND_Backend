# social/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache #for storig session token
from .models import OneToOneMessage,GroupMessage,ChatGroup
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

