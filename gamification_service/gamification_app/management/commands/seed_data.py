import uuid
from django.core.management.base import BaseCommand
from gamification_app.models import (
    UserAccount, Interest, UserInterest, Profile, GamificationQuestion
)


class Command(BaseCommand):
    help = "Seed initial dummy data for all gamification tables"

    def handle(self, *args, **kwargs):
        # --- 1. Create UserAccounts ---
        users_data = [
            {"name": "Alice", "email": "alice@example.com", "phone": "1234567890", "bio": "Love coding", "gender": "Female"},
            {"name": "Bob", "email": "bob@example.com", "phone": "9876543210", "bio": "Music lover", "gender": "Male"},
        ]
        users = []
        for data in users_data:
            user, _ = UserAccount.objects.get_or_create(
                email=data["email"],
                defaults=data
            )
            users.append(user)
            self.stdout.write(self.style.SUCCESS(f"User added: {user.email}"))

        # --- 2. Create Interests ---
        interests_data = ["Coding", "Music", "Sports", "Traveling"]
        interests = []
        for interest_name in interests_data:
            interest, _ = Interest.objects.get_or_create(interestName=interest_name)
            interests.append(interest)
            self.stdout.write(self.style.SUCCESS(f"Interest added: {interest.interestName}"))

        # --- 3. Assign Interests to Users ---
        if users and interests:
            for user in users:
                for interest in interests[:2]:  # assign first 2 interests to each user
                    UserInterest.objects.get_or_create(
                        userId=user,
                        InterestId=interest
                    )
                    self.stdout.write(self.style.SUCCESS(f"Assigned {interest} to {user.email}"))

        # --- 4. Create Profiles ---
        profiles_data = [
            {"userId": users[0], "userName": "alice123", "emoji": "😊", "about": "Passionate about tech", "location": "Kerala"},
            {"userId": users[1], "userName": "bob_the_builder", "emoji": "🎵", "about": "Guitarist", "location": "Bangalore"},
        ]
        for data in profiles_data:
            profile, _ = Profile.objects.get_or_create(userId=data["userId"], defaults=data)
            self.stdout.write(self.style.SUCCESS(f"Profile created for {profile.userName}"))

        # --- 5. Create Gamification Questions ---
        questions_data = [
            {"field_name": "emoji", "questions_text": "Choose an emoji that best describes you", "points": 5},
            {"field_name": "about", "questions_text": "Tell us a short bio about yourself", "points": 10},
            {"field_name": "profileImageUrl", "questions_text": "Upload your profile picture", "points": 10},
            {"field_name": "location", "questions_text": "Where are you currently located?", "points": 5},
            {"field_name": "dob", "questions_text": "Enter your date of birth", "points": 10},
            {"field_name": "gender", "questions_text": "Select your gender", "points": 5},
            {"field_name": "audioUrl", "questions_text": "Record a short audio intro", "points": 15},
            {"field_name": "interests", "questions_text": "Select your interests", "points": 15},

        ]
        for item in questions_data:
            obj, created = GamificationQuestion.objects.get_or_create(
                field_name=item["field_name"],
                defaults={
                    "questions_text": item["questions_text"],
                    "points": item["points"],
                    "is_active": True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added gamification question: {obj}"))
            else:
                self.stdout.write(self.style.WARNING(f"Skipped (already exists): {obj}"))

        self.stdout.write(self.style.SUCCESS("✅ Dummy data inserted successfully"))
