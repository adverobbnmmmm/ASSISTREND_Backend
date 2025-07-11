from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import authenticate
from rest_framework import status, permissions, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import  UserAccount, Profile, Interest, UserInterest
from .serializers import (
    UserRegistrationSerializer, OTPSerializer, LoginSerializer, UserDetailSerializer,
    ProfileSetupSerializer, InterestSerializer, ProfileSerializer
)
from .utils import generateOtp, sendOtpEmail,sendOtpSMS
from django.core.cache import cache
from rest_framework.decorators import api_view

class RegisterView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        print("############## Request Data: ", request.data)
        serializer = UserRegistrationSerializer(data=request.data)
        print("#################serializer.is_valid()",serializer.is_valid())
        if serializer.is_valid():
            validated_data = serializer.validated_data
            print("############# validated_data",validated_data["name"],validated_data["email"],validated_data["phone"])
            # Generate and send OTP
            otp = generateOtp()
            sendOtpEmail(validated_data["email"], otp)
            sendOtpSMS(validated_data["phone"], otp)
            # Store OTP in cache (expires in 5 minutes)
            cache.set(f"otp_{validated_data["email"]}", otp, timeout=300)
            cache.set(f"otp_{validated_data["phone"]}", otp, timeout=300)
            cache.set(f"user_data_{validated_data['email']}", validated_data, timeout=300)
            return Response({"message": "Check your email or phone for OTP."}, status=status.HTTP_201_CREATED)
        print("#################serializer.errors",serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPVerifyView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otpCode = serializer.validated_data['otpCode']

            # Retrieve OTP from cache
            cached_otp = cache.get(f"otp_{email}")
            cached_user_data = cache.get(f"user_data_{email}")

            if cached_otp is None:
                return Response({"message": "OTP expired."}, status=status.HTTP_400_BAD_REQUEST)
            if cached_otp != otpCode:
                return Response({"message": "OTP not matching!"}, status=status.HTTP_400_BAD_REQUEST)
            if cached_user_data and cached_otp == otpCode:
                cache.delete(f"otp_{email}")  # Remove OTP after successful verification
                cache.delete(f"user_data_{email}")
                # Save the user data to the database
                user = UserAccount.objects.create(
                    name=cached_user_data['name'],
                    email=cached_user_data['email'],
                    phone=cached_user_data['phone'],
                    description=cached_user_data.get('description', '')
                )
                
                user.set_password(cached_user_data['password'])
                user.privacy_policy_accepted = cached_user_data['privacy_policy_accepted']
                user.save()
                
                refresh = RefreshToken.for_user(user)
                return Response({'refresh': str(refresh), 'access': str(refresh.access_token),
                        'userId': user.id}, status=status.HTTP_200_OK)
                
                # Note: This code is unreachable
                # return Response({"message": "OTP verified!,Account creation successful"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the token
            
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

@api_view(['POST'])
def setupProfile(request):
    """
    View to setup user profile after OTP verification.
    This function will handle the logic to create a profile for the user.
    """
    print(f'DEBUG: setupProfile called with data: {request.data}')
    
    try:
        user_id = request.data.get('userId')
        print(f'DEBUG: Extracted userId: {user_id}')
        
        if not user_id:
            print('DEBUG: No userId provided')
            return Response({'status': 'error', 'message': 'User ID is required.'}, status=400)
        
        user = UserAccount.objects.get(id=user_id)
        print(f'DEBUG: Found user: {user.email}')
        
        # Check if profile already exists
        if Profile.objects.filter(userId=user).exists():
            print('DEBUG: Profile already exists')
            return Response({'status': 'error', 'message': 'Profile already exists.'}, status=400)
        
        print('DEBUG: Creating serializer with context')
        serializer = ProfileSetupSerializer(data=request.data, context={'user': user})
        
        if serializer.is_valid():
            print('DEBUG: Serializer is valid, saving profile')
            profile = serializer.save()
            print(f'DEBUG: Profile saved successfully: {profile.id}')
            return Response({'status': 'success', 'message': 'Profile setup completed successfully.'})
        else:
            print(f'DEBUG: Serializer errors: {serializer.errors}')
            return Response({'status': 'error', 'message': 'Invalid data', 'errors': serializer.errors}, status=400)
    
    except UserAccount.DoesNotExist:
        print(f'DEBUG: UserAccount with id {user_id} not found')
        return Response({'status': 'error', 'message': 'User not found.'}, status=404)
    except Exception as e:
        print(f'DEBUG: Exception in setupProfile: {str(e)}')
        return Response({'status': 'error', 'message': str(e)}, status=500)

@api_view(['GET'])
def getInterests(request):
    """
    View to get all available interests.
    This function will return all interests that users can select from.
    """
    interests = Interest.objects.all()
    serializer = InterestSerializer(interests, many=True)
    return Response({'status': 'success', 'interests': serializer.data})

@api_view(['GET'])
def checkProfileExists(request):
    """
    View to check if a user's profile exists.
    This function will check if the user has completed profile setup.
    """
    user_id = request.GET.get('userId')
    print(f'DEBUG: checkProfileExists called with userId: {user_id}')
    
    if not user_id:
        print('DEBUG: No userId provided')
        return Response({'status': 'error', 'message': 'User ID is required.'}, status=400)
    
    try:
        # Get the UserAccount object first
        user = UserAccount.objects.get(id=user_id)
        print(f'DEBUG: Found user: {user.email}')
        
        # Check if a Profile exists for this UserAccount
        profile_exists = Profile.objects.filter(userId=user).exists()
        print(f'DEBUG: Profile exists: {profile_exists}')
        
        return Response({'status': 'success', 'profileExists': profile_exists})
    except UserAccount.DoesNotExist:
        print(f'DEBUG: UserAccount with id {user_id} not found')
        return Response({'status': 'error', 'message': 'User not found.'}, status=404)

@api_view(['GET'])
def getUserProfile(request):
    """
    View to get user profile data.
    This function will return the user's profile information.
    """
    user_id = request.GET.get('userId')
    if not user_id:
        return Response({'status': 'error', 'message': 'User ID is required.'}, status=400)
    
    try:
        user = UserAccount.objects.get(id=user_id)
        profile = Profile.objects.get(userId=user)
        serializer = ProfileSerializer(profile)
        return Response({'status': 'success', 'profile': serializer.data})
    except UserAccount.DoesNotExist:
        return Response({'status': 'error', 'message': 'User not found.'}, status=404)
    except Profile.DoesNotExist:
        return Response({'status': 'error', 'message': 'Profile not found.'}, status=404)

@api_view(['GET'])
def testDatabase(request):
    """
    Test endpoint to check database connectivity and table structure
    """
    try:
        # Test UserAccount table
        user_count = UserAccount.objects.count()
        print(f'DEBUG: UserAccount table has {user_count} records')
        
        # Test Profile table
        profile_count = Profile.objects.count()
        print(f'DEBUG: Profile table has {profile_count} records')
        
        # Test Interest table
        interest_count = Interest.objects.count()
        print(f'DEBUG: Interest table has {interest_count} records')
        
        return Response({
            'status': 'success',
            'message': 'Database connection successful',
            'counts': {
                'users': user_count,
                'profiles': profile_count,
                'interests': interest_count
            }
        })
    except Exception as e:
        print(f'DEBUG: Database test error: {str(e)}')
        return Response({
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }, status=500)

