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