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
        managed = False  # Tell Django not to manage this table
        db_table = 'app_userinterest'  # Specify the exact table name in the database


class Interest(models.Model):
    interestName=models.CharField(max_length=255, blank=False, null=False)
    
    
    class Meta:
        managed = False
        db_table = 'app_interest'  # Specify the exact table name in the database
        
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

    class Meta:
        managed = False  # Tell Django not to manage this table
        db_table = 'app_profile'  # Specify the exact table name in the database
    
   
class HighlightQuestion(models.Model):
    question = models.TextField()


class Highlight(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    question = models.ForeignKey(HighlightQuestion, on_delete=models.CASCADE)
    user_response = models.TextField()


class SocialLink(models.Model):
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('other', 'Other'),
    ]   
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    url = models.URLField()

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.URLField()

class UserBadge(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    date_awarded = models.DateTimeField(auto_now_add=True)

class Trophy(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.URLField()

class UserTrophy(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    trophy = models.ForeignKey(Trophy, on_delete=models.CASCADE)
    date_awarded = models.DateTimeField(auto_now_add=True)

class PostCategory(models.Model):
    name = models.CharField(max_length=100)

class Post(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    caption = models.TextField(blank=True)
    image_url = models.URLField()
    category = models.ForeignKey(PostCategory, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class TaggedPerson(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)

class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'user')

class PostComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Story(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()