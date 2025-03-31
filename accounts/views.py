from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import authenticate
from rest_framework import status, permissions, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import  UserAccount
from .serializers import UserRegistrationSerializer, OTPSerializer, LoginSerializer, UserDetailSerializer
from .utils import generateOtp, sendOtpEmail,sendOtpSMS
from django.core.cache import cache

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
                return Response({"message": "OTP verified!,Account creation successful"}, status=status.HTTP_200_OK)
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

