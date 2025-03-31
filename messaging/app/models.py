from django.db import models

import uuid

class Message1to1(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='received_messages')
    message_type = models.CharField(
        max_length=10,
        choices=[('text', 'Text'), ('image', 'Image'), ('audio', 'Audio')]
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    read_status = models.BooleanField(default=False)
    encrypted_conversation = models.TextField(blank=True, null=True)
    delete_settings = models.JSONField(blank=True, null=True)
    reply_to_message_id = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_timestamp = models.DateTimeField(blank=True, null=True)

class MessageGroup(models.Model):
    group_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_name = models.CharField(max_length=255)
    group_description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=10,
        choices=[('admin', 'Admin'), ('member', 'Member')]
    )
    encrypted_conversation = models.TextField(blank=True, null=True)
    delete_settings = models.JSONField(blank=True, null=True)
    admin = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='admin_groups')
    is_deleted = models.BooleanField(default=False)
    deleted_timestamp = models.DateTimeField(blank=True, null=True)