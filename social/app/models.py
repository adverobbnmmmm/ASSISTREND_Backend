import uuid
from django.db import models

# Create your models here.
class Connect(models.Model):
    connect_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='connections')
    initiator_user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='initiated_connections')
    connection_status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending'
    )
    connection_timestamp = models.DateTimeField(auto_now_add=True)

class Friend(models.Model):
    friend_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='friends')
    friend_user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='friend_requests')
    accepted = models.BooleanField(default=False)
    requested = models.BooleanField(default=True)
    friendship_timestamp = models.DateTimeField(auto_now_add=True)
    # Prevent duplicate friend relationships 
    class Meta:
        unique_together = [['user', 'friend_user']]

class Notification(models.Model):
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='notifications')
    source_user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='sent_notifications')
    type = models.CharField(
        max_length=25,
        choices=[('friend_request', 'Friend Request'), ('message', 'Message'), ('challenge_completion', 'Challenge Completion'), ('reaction', 'Reaction')]
    )
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    privacy_setting = models.CharField(
        max_length=15,
        choices=[('public', 'Public'), ('private', 'Private'), ('friends_only', 'Friends Only')]
    )
    pic = models.ImageField(upload_to='post_images/', blank=True, null=True)
    saved = models.BooleanField(default=False)
    audio = models.FileField(upload_to='post_audio/', blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    tag = models.CharField(max_length=255, blank=True, null=True)
    queued = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

class Engagement(models.Model):
    engagement_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=10,
        choices=[('like', 'Like'), ('love', 'Love')]
    )
    timestamp = models.DateTimeField(auto_now_add=True)

class Status(models.Model):
    status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    badge = models.CharField(max_length=255, blank=True, null=True)
    point = models.IntegerField(default=0)
    challenge_track = models.ForeignKey(ChallengeTrack, on_delete=models.SET_NULL, null=True, blank=True) # Double Check
    expiry_date = models.DateField(blank=True, null=True)