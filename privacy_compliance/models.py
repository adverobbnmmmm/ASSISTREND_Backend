from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class PrivacyConsent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='privacy_consent')
    accepted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consent from {self.user.username} on {self.accepted_at}"
