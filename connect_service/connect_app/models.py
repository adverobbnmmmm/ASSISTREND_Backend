# connect_app/models.py
from django.db import models

class UserAccount(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    bio = models.CharField(max_length=255, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
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
    password = models.CharField(max_length=128)

    class Meta:
        managed = True

    def __str__(self):
        return self.email


class Interest(models.Model):
    # kept your field name interestName to be compatible with existing DB
    interestName = models.CharField(max_length=255, blank=False, null=False)
    class Meta:
        managed = True
    def __str__(self):
        return self.interestName


class UserInterest(models.Model):
    # permanent user profile interests (existing)
    userId = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='userinterests')
    interestId = models.ForeignKey(Interest, on_delete=models.CASCADE, related_name='userinterests')
    class Meta:
        managed = True
        unique_together = ('userId', 'interestId')


class InstantInterest(models.Model):
    """
    Temporary instant interests for connect feature.
    Each row = one (user, interest) selection made for the current instant/connect session.
    These are read by other users for matching. They are intended to be short-lived.
    """
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='instant_interests')
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE, related_name='instant_users')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        managed = True
        unique_together = ('user', 'interest')
    def __str__(self):
        return f"{self.user.email} - {self.interest.interestName}"
