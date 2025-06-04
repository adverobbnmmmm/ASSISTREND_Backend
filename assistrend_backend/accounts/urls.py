from django.http import JsonResponse
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    CustomTokenObtainPairView,
    UserProfileView,
    GoogleLoginView,
    auth_routes
)

urlpatterns = [
    path('', auth_routes, name='auth_routes'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('profile/', UserProfileView.as_view(), name='profile'),

    path('google/', GoogleLoginView.as_view(), name='google_login'),


    path('health/', lambda request: JsonResponse({'status': 'ok'}), name='health_check'),
]