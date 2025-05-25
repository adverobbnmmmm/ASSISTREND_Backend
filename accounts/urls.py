from django.urls import path
from .views import RegisterView, OTPVerifyView, LoginView,LogoutView, UserProfileView



urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify_otp/', OTPVerifyView.as_view(), name='verify_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('friends/', FriendListView.as_view(), name='friend-list'),
    path('friends/add/', AddFriendView.as_view(), name='add-friend'),
    path('friends/remove/<int:friend_id>/', RemoveFriendView.as_view(), name='remove-friend'),
    path('friends/block-toggle/<int:friend_id>/', ToggleBlockFriendView.as_view(), name='block-unblock-friend'),
    path('user-with-profile/', UserWithProfileView.as_view(), name='user-with-profile'),
    path('profile/highlights/', HighlightView.as_view(), name='profile-highlights'),
    path('profile/highlights/visibility/', ToggleHighlightVisibilityView.as_view(), name='highlight-visibility'),
    path('profile/customization/', ThemeLayoutCustomizationView.as_view(), name='theme-layout-customization'),
]