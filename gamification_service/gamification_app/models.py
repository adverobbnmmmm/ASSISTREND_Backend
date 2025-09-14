from django.db import models
import uuid

# Create your models here.

class UserAccount(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255,unique=True)
    phone = models.CharField(max_length=15,blank=True,null=True)
    bio =  models.CharField(max_length=255,blank=True,null=True)
    dob = models.DateField(blank=True,null=True)
    gender = models.CharField(
        max_length=20,
        choices=[('Male','Male'),('Female','Female'),('Other','Other')],
        blank=True,
        null=True
    )
    profilepicture = models.ImageField(upload_to='user_photos/',blank=True,null=True)
    description = models.TextField(blank=True,null=True)
    interest = models.TextField(blank=True,null=True)
    aim = models.JSONField(default=dict,blank=True,null=True)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    privacy_policy_accepted = models.BooleanField(default=False)
    salt = models.CharField(max_length=255,blank=True,null=True)
    location = models.CharField(max_length=255,blank=True,null=True)
    last_updated_timestamp = models.DateTimeField(auto_now=True)
    last_login_timestamp = models.DateTimeField(blank=True,null=True)
    class Meta:
        db_table = 'app_useraccount'
        managed = True
    def __str__(self):
        return self.email

class Interest(models.Model):
    interestName = models.CharField(max_length=255,blank=False,null=True)
    class Meta:
        db_table = 'app_interest'
        managed = True
    def __str__(self):
        return self.interestName

class UserInterest(models.Model):
    userId = models.ForeignKey(UserAccount,on_delete=models.CASCADE,related_name='used_id_interests')
    InterestId = models.ForeignKey(Interest,on_delete=models.CASCADE,related_name='interest_id_interests')
    class Meta:
        db_table = 'app_userinterest'
        managed = True
    def __str__(self):
        return {self.userId.email} - {self.InterestId.interestName}


class Profile(models.Model):
    userId = models.OneToOneField(UserAccount,on_delete=models.CASCADE,related_name='profile')
    userName = models.CharField(max_length=255,blank=False,null=False)
    emoji = models.CharField(max_length=100,blank=True,null=True)
    about = models.CharField(max_length=255,null=True,blank=True)
    points = models.IntegerField(default=0)
    isPrivate = models.BooleanField(default=False)
    profileImageurl = models.URLField(blank=True,null=True)
    location = models.CharField(max_length=255,blank=True,null=True)
    dob = models.DateField(blank=True,null=True)
    gender = models.CharField(max_length=20,choices=[('Male','Male'),('Female','Female'),('Other','Other')])
    audioUrl = models.URLField(blank=True,null=True)
    class Meta:
        db_table = 'app_profile'
        managed = True
    def __str__(self):
        return f"{self.userName} - {self.userId.email}"

def get_profile_field_choices():
    excluded = ['id','userName','userId','isPrivate','points']
    fields = [
        (field.name,field.verbose_name.title().replace("_"," "))
        for field in Profile._meta.fields
        if field.name not in excluded
    ]
    return fields

class GamificationQuestion(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    field_name = models.CharField(max_length=100,unique=True,choices=get_profile_field_choices())
    questions_text = models.CharField(max_length=255,blank=True,null=True)
    points = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table= 'app_gamification_question'
        managed = True
    def __str__(self):
        return f"{self.questions_text} - {self.points}"

