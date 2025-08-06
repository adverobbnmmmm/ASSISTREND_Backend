from django.urls import path
from .views import (
    RegisterView, OTPVerifyView, LoginView, LogoutView, UserProfileView,
    setupProfile, getInterests, checkProfileExists, getUserProfile, testDatabase,checkServerStatus
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify_otp/', OTPVerifyView.as_view(), name='verify_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    
    # Profile setup endpoints
    path('setup-profile/', setupProfile, name='setup_profile'),
    path('get-interests/', getInterests, name='get_interests'),
    path('check-profile/', checkProfileExists, name='check_profile'),
    path('user-profile-detail/', getUserProfile, name='user_profile_detail'),
    path('test-database/', testDatabase, name='test_database'),
    path('checkServerStatus/',checkServerStatus,name='check_server_status')
]