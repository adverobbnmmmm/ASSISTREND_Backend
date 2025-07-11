from rest_framework import serializers
from .models import Post, PostLike, PostComment, Profile, UserAccount, Interest, UserInterest

class PostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.name', read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post

        fields = ['id', 'user', 'username', 'caption', 'image_url', 'audio_url', 'category', 'created_at', 'likes_count', 'is_liked', 'comments_count']

    def get_likes_count(self, obj):
        return PostLike.objects.filter(post=obj).count()

    def get_is_liked(self, obj):
        # Expect user_id to be passed in serializer context
        user_id = self.context.get('user_id')
        if not user_id:
            return False
        return PostLike.objects.filter(post=obj, user_id=user_id).exists()

    def get_comments_count(self, obj):
        return PostComment.objects.filter(post=obj).count()


class ProfileSetupSerializer(serializers.ModelSerializer):
    interests = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Profile
        fields = ['userName', 'emoji', 'about', 'location', 'dob', 'gender', 'profileImageUrl', 'audioUrl', 'interests']
        
    def create(self, validated_data):
        interests_data = validated_data.pop('interests', [])
        user = self.context['user']  # Get user from context
        
        # Create profile
        profile = Profile.objects.create(userId=user, **validated_data)
        
        # Handle interests
        if interests_data:
            for interest_name in interests_data:
                interest, created = Interest.objects.get_or_create(
                    interestName=interest_name
                )
                UserInterest.objects.create(
                    userId=user,
                    interestId=interest
                )
        
        return profile


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'interestName']


class ProfileSerializer(serializers.ModelSerializer):
    interests = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = ['userName', 'emoji', 'about', 'points', 'isPrivate', 'profileImageUrl', 'location', 'dob', 'gender', 'audioUrl', 'interests']
        
    def get_interests(self, obj):
        user_interests = UserInterest.objects.filter(userId=obj.userId).select_related('interestId')
        return [ui.interestId.interestName for ui in user_interests]

