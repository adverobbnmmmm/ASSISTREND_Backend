from rest_framework import serializers
from .models import Post, PostLike, PostComment, Profile, UserAccount, Interest, UserInterest

class PostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.name', read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    posterProfileImageUrl = serializers.CharField(source='user.profile.profileImageUrl', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'username', 'caption', 'image_url', 'audio_url', 'category', 'created_at', 'likes_count', 'is_liked', 'comments_count', 'posterProfileImageUrl']

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
        extra_kwargs = {
            'userName': {'required': True},  # Explicitly make userName required
            'emoji': {'required': False},
            'about': {'required': False},
            'location': {'required': False},
            'dob': {'required': False},
            'gender': {'required': False},
            'profileImageUrl': {'required': False},
            'audioUrl': {'required': False},
        }
        
    def create(self, validated_data):
        print(f'DEBUG: ProfileSetupSerializer.create called with: {validated_data}')
        
        interests_data = validated_data.pop('interests', [])
        user = self.context['user']  # Get user from context
        
        print(f'DEBUG: User from context: {user.email}')
        print(f'DEBUG: Interests data: {interests_data}')
        print(f'DEBUG: Validated data after popping interests: {validated_data}')
        
        # Create profile
        try:
            profile = Profile.objects.create(userId=user, **validated_data)
            print(f'DEBUG: Profile created successfully with ID: {profile.id}')
        except Exception as e:
            print(f'DEBUG: Error creating profile: {str(e)}')
            raise
        
        # Handle interests
        if interests_data:
            print(f'DEBUG: Processing {len(interests_data)} interests')
            for interest_name in interests_data:
                print(f'DEBUG: Processing interest: {interest_name}')
                interest, created = Interest.objects.get_or_create(
                    interestName=interest_name
                )
                print(f'DEBUG: Interest {"created" if created else "found"}: {interest.interestName}')
                
                user_interest = UserInterest.objects.create(
                    userId=user,
                    interestId=interest
                )
                print(f'DEBUG: UserInterest created: {user_interest.id}')
        
        print(f'DEBUG: Profile setup completed for user: {user.email}')
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

