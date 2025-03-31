from django.db import models

import uuid

class Challenge(models.Model):
    challenge_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=15,
        choices=[('active', 'Active'), ('completed', 'Completed'), ('expired', 'Expired')]
    )

class ChallengeTrack(models.Model):
    track_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    progress = models.JSONField(blank=True, null=True)
    completion_status = models.CharField(
        max_length=15,
        choices=[('in_progress', 'In Progress'), ('completed', 'Completed')]
    )
    timestamp = models.DateTimeField(auto_now_add=True)

class Leaderboard(models.Model):
    leaderboard_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    badge = models.CharField(max_length=255, blank=True, null=True)
    point = models.IntegerField(default=0)
    status = models.CharField(
        max_length=10,
        choices=[('active', 'Active'), ('inactive', 'Inactive')]
    )
    timestamp = models.DateTimeField(auto_now_add=True)
