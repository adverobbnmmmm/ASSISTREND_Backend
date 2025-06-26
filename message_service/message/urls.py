from django.urls import path
from .views import(
    RequestSocketSession,
    GetMissedChats,
    SendFriendRequest,
    RespondToFriendRequest,
    PendingFriendRequests
)

urlpatterns = [
    path('api/socket-session',RequestSocketSession.as_view(),name='request_socket_session'),
    path('api/missed-messages/', GetMissedChats.as_view(), name='missed-messages'),
    # Send a friend request to a user (POST)
    path('api/friends/request/', SendFriendRequest.as_view(), name='send_friend_request'),
    # Accept or reject a friend request (POST)
    path('api/friends/respond/', RespondToFriendRequest.as_view(), name='respond_to_friend_request'),
    # Get list of pending friend requests for the logged-in user (GET)
    path('api/friends/pending/', PendingFriendRequests.as_view(), name='pending_friend_requests'),

]