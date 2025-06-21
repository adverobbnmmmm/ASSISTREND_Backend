from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.getProfile, name='get_profile'),
    path('update-about/', views.updateAbout, name='update_about'),
    path('update-emoji/', views.updateEmoji, name='update_emoji'),
    path('update-name/', views.updateName, name='update_name'),
    path('update-socials/', views.updateSocials, name='update_socials'),
    path('update-interests/', views.updateInterests, name='update_interests'),
]