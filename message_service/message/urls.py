from django.urls import path
from .views import(
    AvailableChatsView,
    GetMissedChats,
    SendFriendRequest,
    RespondToFriendRequest,
    PendingFriendRequests,
    UserSearchView
)

urlpatterns = [
    path('api/missed-messages/', GetMissedChats.as_view(), name='missed-messages'),
    # Send a friend request to a user (POST)
    path('api/friends/request/', SendFriendRequest.as_view(), name='send_friend_request'),
    # Accept or reject a friend request (POST)
    path('api/friends/respond/', RespondToFriendRequest.as_view(), name='respond_to_friend_request'),
    # Get list of pending friend requests for the logged-in user (GET)
    path('api/friends/pending/', PendingFriendRequests.as_view(), name='pending_friend_requests'),
    path('api/search/users/',UserSearchView.as_view(),name='user-search'),
    #Gives the friends and groups user have.
    path("api/chats/available/", AvailableChatsView.as_view(), name="available-chats"),
]