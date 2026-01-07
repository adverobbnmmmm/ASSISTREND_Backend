#!/usr/bin/env python
"""
Test script for Profile Setup API endpoints
Run this from the social_service directory
"""
import os
import sys
import django
import json
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_service.settings')
django.setup()

from features.models import UserAccount, Profile, Interest, UserInterest
from features.serializers import ProfileSetupSerializer, InterestSerializer

def test_profile_setup():
    """Test the profile setup functionality"""
    print("Testing Profile Setup API...")
    
    # Create a test user (normally this would come from the accounts service)
    test_user_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'phone': '1234567890',
        'password': 'testpassword123',
        'is_active': True,
        'privacy_policy_accepted': True,
    }
    
    # Create or get test user
    user, created = UserAccount.objects.get_or_create(
        email=test_user_data['email'],
        defaults=test_user_data
    )
    
    if created:
        print(f"✓ Created test user: {user.email}")
    else:
        print(f"✓ Using existing test user: {user.email}")
    
    # Test profile setup
    profile_data = {
        'userName': 'testuser123',
        'emoji': '😊',
        'about': 'This is a test user profile',
        'location': 'Test City',
        'dob': '1990-01-01',
        'gender': 'Male',
        'profileImageUrl': 'https://example.com/test.jpg',
        'audioUrl': 'https://example.com/test.mp3',
        'interests': ['Technology', 'Music', 'Sports']
    }
    
    # Remove existing profile if it exists
    Profile.objects.filter(userId=user).delete()
    UserInterest.objects.filter(userId=user).delete()
    
    # Test the serializer
    serializer = ProfileSetupSerializer(data=profile_data, context={'user': user})
    
    if serializer.is_valid():
        profile = serializer.save()
        print(f"✓ Created profile: {profile.userName}")
        
        # Check if interests were created
        user_interests = UserInterest.objects.filter(userId=user)
        print(f"✓ Created {user_interests.count()} interests for user")
        
        for ui in user_interests:
            print(f"  - {ui.interestId.interestName}")
            
    else:
        print(f"✗ Profile setup failed: {serializer.errors}")
        return False
    
    # Test getting interests
    all_interests = Interest.objects.all()
    print(f"✓ Total interests in database: {all_interests.count()}")
    
    # Test profile exists check
    profile_exists = Profile.objects.filter(userId=user).exists()
    print(f"✓ Profile exists check: {profile_exists}")
    
    return True

def populate_test_interests():
    """Populate database with test interests"""
    print("Populating test interests...")
    
    interests = [
        'Technology', 'Sports', 'Music', 'Movies', 'Books', 'Travel', 'Food', 
        'Art', 'Photography', 'Gaming', 'Fitness', 'Fashion', 'Science', 
        'Nature', 'Dancing', 'Cooking', 'Writing', 'Languages', 'History', 
        'Politics'
    ]
    
    created_count = 0
    for interest_name in interests:
        interest, created = Interest.objects.get_or_create(
            interestName=interest_name
        )
        if created:
            created_count += 1
    
    print(f"✓ Created {created_count} new interests")
    return True

if __name__ == '__main__':
    print("=== Profile Setup Test Script ===")
    
    # Populate interests first
    populate_test_interests()
    
    # Test profile setup
    if test_profile_setup():
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)
