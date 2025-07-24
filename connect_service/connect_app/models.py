#Django shared tables from accounts service
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
        managed = False  # Tell Django not to manage this table
        db_table = 'app_useraccount'  # Specify the exact table name in the database
    def __str__(self):
        return self.email

class UserInterest(models.Model):
    userId = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    interestId =  models.ForeignKey('Interest', on_delete=models.CASCADE)
    class Meta:
        managed=False
        db_table="app_userinterest"

class Interest(models.Model):
    interestName=models.CharField(max_length=255, blank=False, null=False)
    class Meta:
        managed=False
        db_table="app_interest"
    def __str__(self):
        return self.interestName
        