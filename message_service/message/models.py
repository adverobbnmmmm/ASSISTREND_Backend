from django.db import models
from django.utils import timezone

# ========================================
# UserAccount model from shared accounts DB
# ========================================
# This model is not managed by Django migrations, but reflects the real table in the shared database
class UserAccount(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    bio = models.CharField(max_length=255, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=20,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        blank=True,
        null=True
    )
    profilepicture = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    interest = models.TextField(blank=True, null=True)
    aim = models.JSONField(default=dict, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    privacy_policy_accepted = models.BooleanField(default=False)
    salt = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    last_updated_timestamp = models.DateTimeField(auto_now=True)
    last_login_timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'accounts_useraccount'  # Link to the exact user table name from the accounts microservice
        managed = False  # Prevent Django from creating/modifying this table via migrations


# ===========================
# Abstract base message model
# ===========================
# Contains shared fields like sender, message text, image, timestamp
class BaseMessage(models.Model):
    sender = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='sent_messages')  # Who sent the message
    message = models.TextField(blank=True, null=True)  # Optional text message
    image = models.ImageField(upload_to="chat_images/", blank=True, null=True)  # Optional image
    sent_time = models.DateTimeField(default=timezone.now)  # Timestamp of when the message was sent

    class Meta:
        abstract = True  # This means this model won’t create its own DB table, but other models can inherit from it


# ===================================
# One-to-One Direct User Messages
# ===================================
# Each message goes from one user to another
class OneToOneMessage(BaseMessage):
    receiver = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='received_one_to_one')  # Receiver of the message
    sent_to_receiver = models.BooleanField(default=False)  # Marks whether receiver has received/read the message

    def is_ready_to_delete(self):
        # If the message has been delivered, we can safely delete it in cleanup tasks
        return self.sent_to_receiver


# =====================
# Group Chat Container
# =====================
# Holds group information and member list
class ChatGroup(models.Model):
    group_name = models.CharField(max_length=255)  # Name/title of the group
    members = models.ManyToManyField(UserAccount, related_name='chat_groups')  # Many users can belong to many groups
    created_at = models.DateTimeField(auto_now_add=True)  # Track creation time
    updated_at = models.DateTimeField(auto_now=True)  # Auto-update when group changes

    def __str__(self):
        return self.group_name


# ===================
# Group Message Model
# ===================
# Represents a message sent to a group
class GroupMessage(BaseMessage):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='messages')  # Which group this message belongs to
    delivered_to = models.ManyToManyField(UserAccount, related_name='delivered_group_messages', blank=True)
    # Keeps track of which users have received this message

    def is_ready_to_delete(self):
        # Only delete if all current group members have received this message
        group_members = self.group.members.all()
        return all(user in self.delivered_to.all() for user in group_members)

    def __str__(self):
        return f"Message by {self.sender} in group {self.group.group_name}"
