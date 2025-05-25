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

class ProfilePictureUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def patch(self, request):
        try:
            image_base64 = request.data.get('profile_image')
            image_name = request.data.get('profile_image_name', 'profile_pic')
            if not image_base64:
                return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)
            if 'base64,' in image_base64:
                image_base64 = image_base64.split('base64,')[1]
            image_data = base64.b64decode(image_base64)
            image_file = ContentFile(image_data, name=f"{image_name}.jpg")
            user = request.user
            user.profilepicture = image_file
            user.save()
            serializer = UserAccountSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserAccountSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user


class UserAccountUpdateView(generics.RetrieveUpdateAPIView):
    queryset = UserAccount.objects.all()
    serializer_class = UserAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user  # Returns current authenticated user

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileDetailUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

class PublicProfilesListView(generics.ListAPIView):
    queryset = Profile.objects.filter(show_activity=True, highlights_visibility='public')
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]


class FriendListView(generics.ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Friend.objects.filter(user=self.request.user)


class AddFriendView(generics.CreateAPIView):
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RemoveFriendView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, friend_id):
        try:
            friendship = Friend.objects.get(user=request.user, friend_id=friend_id)
            friendship.delete()
            return Response({"message": "Friend removed."}, status=status.HTTP_204_NO_CONTENT)
        except Friend.DoesNotExist:
            return Response({"error": "Friend not found."}, status=status.HTTP_404_NOT_FOUND)


class ToggleBlockFriendView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, friend_id):
        try:
            friend = Friend.objects.get(user=request.user, friend_id=friend_id)
            friend.is_blocked = not friend.is_blocked
            friend.save()
            return Response({"blocked": friend.is_blocked})
        except Friend.DoesNotExist:
            return Response({"error": "Friend not found."}, status=status.HTTP_404_NOT_FOUND)


class UserWithProfileView(generics.RetrieveAPIView):
    serializer_class = UserWithProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user


class HighlightView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        return Response({"highlights": profile.highlights})

    def put(self, request):
        profile = Profile.objects.get(user=request.user)
        highlights = request.data.get("highlights", "")
        profile.highlights = highlights
        profile.save()
        return Response({"message": "Highlights updated", "highlights": profile.highlights})


class ToggleHighlightVisibilityView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        profile = Profile.objects.get(user=request.user)
        visibility = request.data.get("visibility", "").lower()
        if visibility not in ["public", "private"]:
            return Response({"error": "Invalid visibility option"}, status=400)
        profile.highlights_visibility = visibility
        profile.save()
        return Response({"message": f"Highlight visibility set to {visibility}"})


class ThemeLayoutCustomizationView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request):
        profile = Profile.objects.get(user=request.user)
        theme = request.data.get("theme")
        layout = request.data.get("layout")
        if theme:
            profile.theme = theme
        if layout:
            profile.layout = layout

        profile.save()
        return Response({
            "message": "Theme and layout updated",
            "theme": profile.theme,
            "layout": profile.layout
        })