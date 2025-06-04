from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
)

CustomUser = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    Register new users with email/password
    POST /api/auth/register/
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        # Generate JWT tokens for immediate login after registration
        refresh = CustomTokenObtainPairSerializer.get_token(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserProfileSerializer(user).data
        }

        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Login users and return JWT tokens
    POST /api/auth/login/
    """
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update user profile
    GET/PUT /api/auth/profile/
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class GoogleLoginView(SocialLoginView):
    """
    Google OAuth2 login
    POST /api/auth/google/
    Requires: { "access_token": "<GOOGLE_TOKEN>", "id_token": "<GOOGLE_ID_TOKEN>" }
    """
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = 'postmessage'  # Important for Flutter apps

    def post(self, request, *args, **kwargs):
        # Add custom response with user data
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            from rest_framework_simplejwt.tokens import RefreshToken
            user = self.request.user
            refresh = RefreshToken.for_user(user)

            response.data.update({
                'user': UserProfileSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            })

        return response


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def auth_routes(request):
    """
    Available authentication endpoints
    GET /api/auth/
    """
    routes = [
        {'POST': '/api/auth/register/', 'description': 'Register new user'},
        {'POST': '/api/auth/login/', 'description': 'Login with JWT'},
        {'POST': '/api/auth/google/', 'description': 'Google OAuth2 login'},
        {'GET/PUT': '/api/auth/profile/', 'description': 'User profile'},
    ]
    return Response(routes)