from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager,AbstractUser,Group, Permission



class UserAccountManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name)

        user.set_password(password)
        user.save()

        return user
    
    def create_superuser(self, email, name, password):
        user = self.create_user(email, name, password)

        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user

class UserAccount(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    bio = models.CharField(max_length=255, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)
    profilepicture = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    interest = models.TextField(blank=True, null=True)  # User interests
    aim = models.JSONField(default=dict, blank=True, null=True)  # JSON field to store {pic, audio}
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    privacy_policy_accepted = models.BooleanField(default=False)
    salt = models.CharField(max_length=255, blank=True, null=True)  # Used for encryption/security purposes
    location = models.CharField(max_length=255, blank=True, null=True)  # Store user location
    last_updated_timestamp = models.DateTimeField(auto_now=True)  # Auto-updated timestamp
    last_login_timestamp = models.DateTimeField(blank=True, null=True)  # Track user's last login


    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    groups = models.ManyToManyField(
        Group,
        related_name="useraccount_set",  # Avoids clashes with the default auth model
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="useraccount_set",  # Avoids clashes with the default auth model
        blank=True
    )

    def get_full_name(self):
        return self.name
    
    def get_short_name(self):
        return self.name
    
    def __str__(self):
        return self.email


class Profile(models.Model):
    userId= models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name='profile')
    userName = models.CharField(max_length=255, blank=False, null=False)
    emoji=models.CharField(max_length=100, blank=True, null=True)
    about=models.TextField(blank=True, null=True)
    points = models.IntegerField(default=0)
    isPrivate = models.BooleanField(default=False)
    profileImageUrl = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)  
    dob= models.DateField(blank=True, null=True)
    gender= models.CharField(max_length=20, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)




class Interest(models.Model):
    interestName=models.CharField(max_length=255, blank=False, null=False)
    
class UserInterest(models.Model):
    userId = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='user_interests')
    interestId = models.ForeignKey(Interest, on_delete=models.CASCADE, related_name='user_interests')
    
    class Meta:
        unique_together = ('userId', 'interestId')  



