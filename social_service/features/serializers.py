from rest_framework import serializers
from .models import Post, PostLike

class PostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.name', read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post

        fields = ['id', 'user', 'username', 'caption', 'image_url', 'audio_url','category', 'created_at', 'likes_count', 'is_liked']

    def get_likes_count(self, obj):
        return PostLike.objects.filter(post=obj).count()

    def get_is_liked(self, obj):
        # Expect user_id to be passed in serializer context
        user_id = self.context.get('user_id')
        if not user_id:
            return False
        return PostLike.objects.filter(post=obj, user_id=user_id).exists()

