from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
import re

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
    print('password successfull')
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