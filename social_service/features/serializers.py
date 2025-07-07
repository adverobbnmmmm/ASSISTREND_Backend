from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'user', 'username', 'caption', 'image_url', 'category', 'created_at']