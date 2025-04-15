# challenge/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChallengeViewSet, ChallengeTrackViewSet, LeaderboardViewSet

router = DefaultRouter()
router.register(r'challenges', ChallengeViewSet)
router.register(r'tracks', ChallengeTrackViewSet)
router.register(r'leaderboards', LeaderboardViewSet)

urlpatterns = [

] + router.urls