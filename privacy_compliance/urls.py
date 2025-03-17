from django.urls import path
from .views import privacy_policy_consent_view, privacy_policy_view

urlpatterns = [
    path('privacy-consent/', privacy_policy_consent_view, name='privacy_policy_consent'),
    path('privacy-policy/', privacy_policy_view, name='privacy_policy'),  # Add this line
]
