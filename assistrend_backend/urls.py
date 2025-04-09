"""
URL configuration for AssistrendBackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt import views as jwt_views
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.instagram.views import InstagramOAuth2Adapter
from allauth.socialaccount.providers.linkedin_oauth2.views import LinkedInOAuth2Adapter

class LinkedInLogin(SocialLoginView):
    adapter_class = LinkedInOAuth2Adapter

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter

class InstagramLogin(SocialLoginView):
    adapter_class = InstagramOAuth2Adapter

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify'),
    path('api/account/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('auth/facebook/', FacebookLogin.as_view(), name='facebook_login'),
    path('auth/instagram/', InstagramLogin.as_view(), name='instagram_login'),
    path('auth/linkedin/', LinkedInLogin.as_view(), name='linkedin_login'),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/social/', include('allauth.socialaccount.urls')),

]
