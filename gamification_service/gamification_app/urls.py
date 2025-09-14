from django.urls import path
from .views import GamificationPointsUpdateView
urlpatterns = [
    path('gamification-points/',GamificationPointsUpdateView.as_view(),name='gamification-update')
]