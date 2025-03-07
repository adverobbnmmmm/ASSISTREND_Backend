from django.urls import path
from .views import RegisterView, OTPVerifyView, LoginView,LogoutView, UserProfileView



urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify_otp/', OTPVerifyView.as_view(), name='verify_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
]