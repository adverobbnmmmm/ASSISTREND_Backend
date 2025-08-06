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
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions

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
    print(f'DEBUG ACCOUNTS: setupProfile called')
    print(f'DEBUG ACCOUNTS: Request method: {request.method}')
    print(f'DEBUG ACCOUNTS: Request data type: {type(request.data)}')
    print(f'DEBUG ACCOUNTS: Request data: {request.data}')
    print(f'DEBUG ACCOUNTS: Request headers: {dict(request.headers)}')
    
    try:
        user_id = request.data.get('userId')
        print(f'DEBUG ACCOUNTS: Extracted userId: {user_id} (type: {type(user_id)})')
        
        if not user_id:
            print('DEBUG ACCOUNTS: No userId provided')
            return Response({'status': 'error', 'message': 'User ID is required.'}, status=400)
        
        # Convert user_id to int if it's a string
        try:
            user_id = int(user_id)
            print(f'DEBUG ACCOUNTS: Converted userId to int: {user_id}')
        except (ValueError, TypeError):
            print(f'DEBUG ACCOUNTS: Could not convert userId to int: {user_id}')
            return Response({'status': 'error', 'message': 'Invalid User ID format.'}, status=400)
        
        print(f'DEBUG ACCOUNTS: Looking for UserAccount with id: {user_id}')
        user = UserAccount.objects.get(id=user_id)
        print(f'DEBUG ACCOUNTS: Found user: {user.email} (id: {user.id})')
        
        # Check if profile already exists
        existing_profile = Profile.objects.filter(userId=user).first()
        if existing_profile:
            print(f'DEBUG ACCOUNTS: Profile already exists with id: {existing_profile.id}')
            return Response({'status': 'error', 'message': 'Profile already exists.'}, status=400)
        else:
            print('DEBUG ACCOUNTS: No existing profile found - proceeding with creation')
        
        print('DEBUG ACCOUNTS: Creating serializer with context')
        serializer = ProfileSetupSerializer(data=request.data, context={'user': user})
        
        print(f'DEBUG ACCOUNTS: Serializer created, validating...')
        if serializer.is_valid():
            print('DEBUG ACCOUNTS: Serializer is valid, calling save()...')
            try:
                profile = serializer.save()
                print(f'DEBUG ACCOUNTS: Profile saved successfully with id: {profile.id}')
                print(f'DEBUG ACCOUNTS: Profile userName: {profile.userName}')
                print(f'DEBUG ACCOUNTS: Profile userId: {profile.userId.id}')
                
                # Verify the profile was actually saved
                verification_profile = Profile.objects.filter(id=profile.id).first()
                if verification_profile:
                    print(f'DEBUG ACCOUNTS: Verification successful - profile exists in database')
                else:
                    print(f'DEBUG ACCOUNTS: WARNING - Profile not found in database after save!')
                
                return Response({'status': 'success', 'message': 'Profile setup completed successfully.', 'profileId': profile.id})
            except Exception as save_error:
                print(f'DEBUG ACCOUNTS: Error during save: {str(save_error)}')
                print(f'DEBUG ACCOUNTS: Save error type: {type(save_error)}')
                return Response({'status': 'error', 'message': f'Error saving profile: {str(save_error)}'}, status=500)
        else:
            print(f'DEBUG ACCOUNTS: Serializer validation failed')
            print(f'DEBUG ACCOUNTS: Serializer errors: {serializer.errors}')
            return Response({'status': 'error', 'message': 'Invalid data', 'errors': serializer.errors}, status=400)
    
    except UserAccount.DoesNotExist:
        print(f'DEBUG ACCOUNTS: UserAccount with id {user_id} not found')
        return Response({'status': 'error', 'message': 'User not found.'}, status=404)
    except Exception as e:
        print(f'DEBUG ACCOUNTS: Unexpected exception in setupProfile: {str(e)}')
        print(f'DEBUG ACCOUNTS: Exception type: {type(e)}')
        import traceback
        print(f'DEBUG ACCOUNTS: Full traceback: {traceback.format_exc()}')
        return Response({'status': 'error', 'message': f'Unexpected error: {str(e)}'}, status=500)

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
    print(f'DEBUG ACCOUNTS: checkProfileExists called with userId: {user_id}')
    
    if not user_id:
        print('DEBUG ACCOUNTS: No userId provided')
        return Response({'status': 'error', 'message': 'User ID is required.'}, status=400)
    
    try:
        # Convert user_id to int if it's a string
        try:
            user_id = int(user_id)
            print(f'DEBUG ACCOUNTS: Converted userId to int: {user_id}')
        except (ValueError, TypeError):
            print(f'DEBUG ACCOUNTS: Could not convert userId to int: {user_id}')
            return Response({'status': 'error', 'message': 'Invalid User ID format.'}, status=400)
        
        # Get the UserAccount object first
        user = UserAccount.objects.get(id=user_id)
        print(f'DEBUG ACCOUNTS: Found user: {user.email} (id: {user.id})')
        
        # Check if a Profile exists for this UserAccount
        profiles = Profile.objects.filter(userId=user)
        profile_count = profiles.count()
        profile_exists = profile_count > 0
        
        print(f'DEBUG ACCOUNTS: Profile query result: {profile_count} profiles found')
        print(f'DEBUG ACCOUNTS: Profile exists: {profile_exists}')
        
        if profile_exists:
            profile = profiles.first()
            print(f'DEBUG ACCOUNTS: Found profile with id: {profile.id}, userName: {profile.userName}')
        
        return Response({'status': 'success', 'profileExists': profile_exists})
    except UserAccount.DoesNotExist:
        print(f'DEBUG ACCOUNTS: UserAccount with id {user_id} not found')
        return Response({'status': 'error', 'message': 'User not found.'}, status=404)
    except Exception as e:
        print(f'DEBUG ACCOUNTS: Exception in checkProfileExists: {str(e)}')
        import traceback
        print(f'DEBUG ACCOUNTS: Full traceback: {traceback.format_exc()}')
        return Response({'status': 'error', 'message': str(e)}, status=500)

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
        print('DEBUG ACCOUNTS: Testing database connectivity...')
        
        # Test UserAccount table
        user_count = UserAccount.objects.count()
        print(f'DEBUG ACCOUNTS: UserAccount table has {user_count} records')
        
        # Show a sample user if exists
        if user_count > 0:
            sample_user = UserAccount.objects.first()
            print(f'DEBUG ACCOUNTS: Sample user: {sample_user.email} (id: {sample_user.id})')
        
        # Test Profile table
        profile_count = Profile.objects.count()
        print(f'DEBUG ACCOUNTS: Profile table has {profile_count} records')
        
        # Show sample profiles if exist
        if profile_count > 0:
            profiles = Profile.objects.all()[:3]  # Show first 3 profiles
            for profile in profiles:
                print(f'DEBUG ACCOUNTS: Profile id: {profile.id}, userName: {profile.userName}, userId: {profile.userId.id}')
        
        # Test Interest table
        interest_count = Interest.objects.count()
        print(f'DEBUG ACCOUNTS: Interest table has {interest_count} records')
        
        # Test UserInterest table
        user_interest_count = UserInterest.objects.count()
        print(f'DEBUG ACCOUNTS: UserInterest table has {user_interest_count} records')
        
        # Try to create a test interest to verify write permissions
        try:
            test_interest, created = Interest.objects.get_or_create(
                interestName='Test Interest for Database Check'
            )
            if created:
                print(f'DEBUG ACCOUNTS: Successfully created test interest with id: {test_interest.id}')
                # Clean up the test interest
                test_interest.delete()
                print(f'DEBUG ACCOUNTS: Successfully deleted test interest')
            else:
                print(f'DEBUG ACCOUNTS: Test interest already existed with id: {test_interest.id}')
        except Exception as e:
            print(f'DEBUG ACCOUNTS: Error testing interest creation: {str(e)}')
        
        return Response({
            'status': 'success',
            'message': 'Database connection successful',
            'counts': {
                'users': user_count,
                'profiles': profile_count,
                'interests': interest_count,
                'user_interests': user_interest_count
            }
        })
    except Exception as e:
        print(f'DEBUG ACCOUNTS: Database test error: {str(e)}')
        import traceback
        print(f'DEBUG ACCOUNTS: Full traceback: {traceback.format_exc()}')
        return Response({
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }, status=500)



@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def checkServerStatus(request):
    """
    Endpoint to check if the server is running.
    """
    return Response({'status': 'Server is running'}, status=status.HTTP_200_OK)