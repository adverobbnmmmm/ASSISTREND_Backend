# challenge/models.py
import uuid
from django.db import models

class Challenge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()  # Refers to user from accounts_service
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=15,
        choices=[('active', 'Active'), ('completed', 'Completed'), ('expired', 'Expired')]
    )

class ChallengeTrack(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField() # Refers to user from accounts_service
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    progress = models.JSONField(blank=True, null=True)
    completion_status = models.CharField(
        max_length=15,
        choices=[('in_progress', 'In Progress'), ('completed', 'Completed')]
    )
    timestamp = models.DateTimeField(auto_now_add=True)

class Leaderboard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField() # Refers to user from accounts_service
    name = models.CharField(max_length=255)
    badge = models.CharField(max_length=255, blank=True, null=True)
    point = models.IntegerField(default=0)
    status = models.CharField(
        max_length=10,
        choices=[('active', 'Active'), ('inactive', 'Inactive')]
    )
    timestamp = models.DateTimeField(auto_now_add=True)