# social/urls.py
from rest_framework.routers import DefaultRouter
from .views import ConnectViewSet, FriendViewSet, PostViewSet, EngagementViewSet, StatusViewSet

router = DefaultRouter()
router.register(r'connects', ConnectViewSet)
router.register(r'friends', FriendViewSet)
router.register(r'posts', PostViewSet)
router.register(r'engagements', EngagementViewSet)
router.register(r'statuses', StatusViewSet)

urlpatterns = [
    
] + router.urls