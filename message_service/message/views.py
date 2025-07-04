# social/views.py

from rest_framework.generics import ListAPIView
from rest_framework import status
from .serializers import UserAccountSerializer
from .pagination import UserScrollPagination
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache #for storig session token
from .models import FriendRequest, Friendship, OneToOneMessage,GroupMessage,ChatGroup, UserAccount
from django.db.models import Q
from .serializers import FriendSerializer, GroupSerializer
import secrets
import datetime


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

class UserSearchView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserAccountSerializer
    pagination_class = UserScrollPagination  # only for this view

    def get_queryset(self):
        query = self.request.GET.get('query', '').strip()
        if not query:
            # Empty query, return empty queryset, no need to send full DB
            return UserAccount.objects.none()
        
        # Only return results matching name or email
        return UserAccount.objects.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query)
        ).order_by('name')

    def list(self, request, *args, **kwargs):
        """
        Override the default list() to return 204 if no results
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            if not page:
                return Response({"detail": "No users found."}, status=status.HTTP_204_NO_CONTENT)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Should not reach here
        return Response({"detail": "Unexpected error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Friendship, ChatGroup


class AvailableChatsView(APIView):#Gives all of the chats the user can have.
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # All friendships involving this user
        friendships = Friendship.objects.filter(
            (Q(user1=user) | Q(user2=user))
        )

        # Extract unique friend users
        friend_ids = set()
        for f in friendships:
            if f.user1_id == user.id:
                friend_ids.add(f.user2_id)
            else:
                friend_ids.add(f.user1_id)

        friends = list(UserAccount.objects.filter(id__in=friend_ids))

        # All groups the user belongs to
        groups = ChatGroup.objects.filter(members=user)

        return Response({
            "friends": FriendSerializer(friends, many=True).data,
            "groups": GroupSerializer(groups, many=True).data
        })
