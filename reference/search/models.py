from django.db import models

class Post(models.Model):
    Title = models.CharField(max_length=255)
    Content = models.TextField()
    Location = models.CharField(max_length=100, blank=True)
    Hashtags = models.CharField(max_length=255, blank=True)
    Created_at = models.DateTimeField(auto_now_add=True)
    Updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title