from django.db import models

import uuid

class Moderator(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField() # Refers to user from accounts_service
    privacy_policy = models.JSONField()
    reports = models.JSONField()
    block = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

class Perk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField() # Refers to user from accounts_service
    name = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Guideline(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
