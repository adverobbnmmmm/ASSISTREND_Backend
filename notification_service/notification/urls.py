# notifications/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet)

urlpatterns = [

] + router.urls