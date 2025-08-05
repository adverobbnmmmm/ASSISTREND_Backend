from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserAccountViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'connect-users', UserAccountViewSet, basename='connect-users')
urlpatterns = [

]+router.urls
