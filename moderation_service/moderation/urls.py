# moderation/urls.py
from rest_framework.routers import DefaultRouter
from .views import ModeratorViewSet, PerkViewSet, GuidelineViewSet

router = DefaultRouter()
router.register(r'moderators', ModeratorViewSet)
router.register(r'perks', PerkViewSet)
router.register(r'guidelines', GuidelineViewSet)

urlpatterns = [

] + router.urls