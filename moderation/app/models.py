from django.db import models

import uuid

class Moderator(models.Model):
    moderation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    privacy_policy = models.JSONField()
    reports = models.JSONField()
    block = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

class Perk(models.Model):
    perk_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Guideline(models.Model):
    guideline_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
