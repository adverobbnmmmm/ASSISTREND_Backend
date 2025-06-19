from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.getProfile, name='get_profile'),
]