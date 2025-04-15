# notifications/models.py
import uuid
from django.db import models

class Notification(models.Model):
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()  # Refers to user from accounts_service
    source_user_id = models.UUIDField()  # Refers to user from accounts_service
    type = models.CharField(
        max_length=25,
        choices=[
            ('friend_request', 'Friend Request'),
            ('message', 'Message'),
            ('challenge_completion', 'Challenge Completion'),
            ('reaction', 'Reaction')
        ]
    )
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)