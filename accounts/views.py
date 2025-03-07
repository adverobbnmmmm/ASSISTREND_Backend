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
        serializer = UserRegistrationSerializer(data=request.data)
        print("#################serializer.is_valid()",serializer.is_valid())
        if serializer.is_valid():
            user = serializer.save()
            print("############# user",user.name,user.email,user.phone)
            # Generate and send OTP
            otp = generateOtp()
            sendOtpEmail(user.email, otp)
            sendOtpSMS(user.phone, otp)
            # Store OTP in cache (expires in 5 minutes)
            cache.set(f"otp_{user.email}", otp, timeout=300)
            cache.set(f"otp_{user.phone}", otp, timeout=300)
            return Response({"message": "User created. Check your email for OTP."}, status=status.HTTP_201_CREATED)
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

            if cached_otp is None:
                return Response({"message": "OTP expired."}, status=status.HTTP_400_BAD_REQUEST)
            if cached_otp != otpCode:
                return Response({"message": "OTP not matching!"}, status=status.HTTP_400_BAD_REQUEST)
            if cached_otp and cached_otp == otpCode:
                cache.delete(f"otp_{email}")  # Remove OTP after successful verification
                return Response({"message": "OTP verified!"}, status=status.HTTP_200_OK)
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

