    # connect_app/urls.py
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import UserAccountViewSet

router = DefaultRouter()
router.register(r'connect-users', UserAccountViewSet, basename='connect-users')

urlpatterns = router.urls
