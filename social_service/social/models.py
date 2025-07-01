# social/models.py
import uuid
from django.db import models

class Connect(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField() # Refers to user from accounts_service
    initiator_user_id = models.UUIDField() # Refers to user from accounts_service
    connection_status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending'
    )
    connection_timestamp = models.DateTimeField(auto_now_add=True)

class Friend(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField() # Refers to user from accounts_service
    friend_user_id = models.UUIDField() # Refers to user from accounts_service
    accepted = models.BooleanField(default=False)
    requested = models.BooleanField(default=True)
    friendship_timestamp = models.DateTimeField(auto_now_add=True)
    # Prevent duplicate friend relationships 
    class Meta:
        unique_together = [['user_id', 'friend_user_id']]

class Engagement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField() # Refers to user from accounts_service
    type = models.CharField(
        max_length=10,
        choices=[('like', 'Like'), ('love', 'Love')]
    )
    timestamp = models.DateTimeField(auto_now_add=True)

class Status(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField() # Refers to user from accounts_service
    title = models.CharField(max_length=255)
    badge = models.CharField(max_length=255, blank=True, null=True)
    point = models.IntegerField(default=0)
    challenge_track_id = models.UUIDField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)