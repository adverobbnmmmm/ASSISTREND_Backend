# social/urls.py
from rest_framework.routers import DefaultRouter
from .views import Message1to1ViewSet, MessageGroupViewSet

router = DefaultRouter()
router.register(r'message-group', MessageGroupViewSet)
router.register(r'message-one-to-one', Message1to1ViewSet)

urlpatterns = [
    
] + router.urls