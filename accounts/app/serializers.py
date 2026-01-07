from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
import re
from .models import UserAccount, Profile, Interest, UserInterest

User = get_user_model()



# User registration serializer (for creating a user with OTP verification)
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        max_length=25,
        validators=[
            RegexValidator(
                regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,25}$',
                message="Password must be 8-25 characters long, include at least one uppercase letter, one lowercase letter, one number, and one special character."
            )
        ]
    )
    privacy_policy_accepted = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = [ 'name','email','phone', 'password',  'description','privacy_policy_accepted']
        extra_kwargs = {'password': {'write_only': True}}
    def validate_privacy_policy_accepted(self, value):
        if not value:
            raise serializers.ValidationError("You must accept the privacy policy to register.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

# OTP Serializer for email verification
class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otpCode = serializers.CharField(max_length=6)

# Serializer to return user data with roles (Admin/User)
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields ='__all__'

# Login Serializer (for obtaining JWT tokens)
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Validate the user and password (You can use Django's `authenticate` method)
        user = authenticate(email=email, password=password)
        # print("111111111111",user)
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        
        if not user.privacy_policy_accepted:
            raise serializers.ValidationError("You must accept the privacy policy before logging in.")
        
        # Create JWT token
        refresh = RefreshToken.for_user(user)
        return {'refresh': str(refresh), 'access': str(refresh.access_token),
                'userId': user.id,
                }

# Profile Setup Serializer
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
            'userName': {'required': True},
            'emoji': {'required': False},
            'about': {'required': False},
            'location': {'required': False},
            'dob': {'required': False},
            'gender': {'required': False},
            'profileImageUrl': {'required': False},
            'audioUrl': {'required': False},
        }
        
    def create(self, validated_data):
        print(f'DEBUG SERIALIZER: ProfileSetupSerializer.create called')
        print(f'DEBUG SERIALIZER: Validated data received: {validated_data}')
        print(f'DEBUG SERIALIZER: Context: {self.context}')
        
        interests_data = validated_data.pop('interests', [])
        user = self.context['user']  # Get user from context
        
        print(f'DEBUG SERIALIZER: User from context: {user.email} (id: {user.id})')
        print(f'DEBUG SERIALIZER: Interests data: {interests_data}')
        print(f'DEBUG SERIALIZER: Validated data after popping interests: {validated_data}')
        
        # Ensure all nullable fields have default values to avoid NULL constraint violations
        profile_data = {
            'userId': user,
            'userName': validated_data.get('userName', ''),
            'emoji': validated_data.get('emoji', ''),
            'about': validated_data.get('about', ''),
            'points': validated_data.get('points', 0),
            'isPrivate': validated_data.get('isPrivate', False),
            'profileImageUrl': validated_data.get('profileImageUrl', ''),
            'location': validated_data.get('location', ''),
            'dob': validated_data.get('dob', None),
            'gender': validated_data.get('gender', ''),
            'audioUrl': validated_data.get('audioUrl', ''),  # Ensure this is never None
        }
        
        print(f'DEBUG SERIALIZER: Final profile data with defaults: {profile_data}')
        
        # Create profile
        try:
            print(f'DEBUG SERIALIZER: About to create Profile with data: {profile_data}')
            
            profile = Profile.objects.create(**profile_data)
            print(f'DEBUG SERIALIZER: Profile created successfully')
            print(f'DEBUG SERIALIZER: Profile ID: {profile.id}')
            print(f'DEBUG SERIALIZER: Profile userName: {profile.userName}')
            print(f'DEBUG SERIALIZER: Profile userId: {profile.userId}')
            print(f'DEBUG SERIALIZER: Profile userId.id: {profile.userId.id}')
            print(f'DEBUG SERIALIZER: Profile audioUrl: {profile.audioUrl}')
            
        except Exception as e:
            print(f'DEBUG SERIALIZER: Error creating profile: {str(e)}')
            print(f'DEBUG SERIALIZER: Error type: {type(e)}')
            import traceback
            print(f'DEBUG SERIALIZER: Full traceback: {traceback.format_exc()}')
            raise
        
        # Handle interests
        if interests_data:
            print(f'DEBUG SERIALIZER: Processing {len(interests_data)} interests')
            try:
                for interest_name in interests_data:
                    print(f'DEBUG SERIALIZER: Processing interest: {interest_name}')
                    interest, created = Interest.objects.get_or_create(
                        interestName=interest_name
                    )
                    print(f'DEBUG SERIALIZER: Interest {"created" if created else "found"}: {interest.interestName} (id: {interest.id})')
                    
                    user_interest = UserInterest.objects.create(
                        userId=user,
                        interestId=interest
                    )
                    print(f'DEBUG SERIALIZER: UserInterest created with id: {user_interest.id}')
            except Exception as e:
                print(f'DEBUG SERIALIZER: Error processing interests: {str(e)}')
                # Don't raise here, as the profile was already created successfully
        
        print(f'DEBUG SERIALIZER: Profile setup completed for user: {user.email}')
        print(f'DEBUG SERIALIZER: Returning profile with id: {profile.id}')
        return profile

# Interest Serializer
class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'interestName']

# Profile Serializer
class ProfileSerializer(serializers.ModelSerializer):
    interests = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = ['userName', 'emoji', 'about', 'points', 'isPrivate', 'profileImageUrl', 'location', 'dob', 'gender', 'audioUrl', 'interests']
        
    def get_interests(self, obj):
        user_interests = UserInterest.objects.filter(userId=obj.userId).select_related('interestId')
        return [ui.interestId.interestName for ui in user_interests]