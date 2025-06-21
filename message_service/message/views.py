# social/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache #for storig session token
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
