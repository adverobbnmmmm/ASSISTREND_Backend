import os
import random
from django.core.files import File
from django.utils import timezone
from django.core.management.base import BaseCommand
from connect_app.models import UserAccount, Interest,UserInterest,InstantInterest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROFILE_PIC_DIR = os.path.join(BASE_DIR, 'media', 'profile_pics')

INTEREST_CATEGORIES = [
    "Accident", "Sports", "College", "Film", "Dropout", "Designing", "Health issue", "Music","Jobless"
]

class Command(BaseCommand):
    help = 'Seed dummy UserAccount users with interests and profile pics'

    def handle(self, *args, **kwargs):
        # ✅ Delete old data
        UserInterest.objects.all().delete()
        Interest.objects.all().delete()
        UserAccount.objects.all().delete()

        # # Optional: Clear old profile pics (DEV only)
        # for filename in os.listdir(PROFILE_PIC_DIR):
        #     file_path = os.path.join(PROFILE_PIC_DIR, filename)
        #     try:
        #         if os.path.isfile(file_path):
        #             os.unlink(file_path)
        #     except Exception as e:
        #         print(f"Error deleting file {file_path}: {e}")

        # ✅ Create Interest objects
        interests = []
        for name in INTEREST_CATEGORIES:
            interest = Interest.objects.create(interestName=name)
            interests.append(interest)

        # ✅ Load available profile pictures
        profile_pics = [
            f for f in os.listdir(PROFILE_PIC_DIR)
            if os.path.isfile(os.path.join(PROFILE_PIC_DIR, f))
        ]

        # ✅ Create Users
        for i in range(10):
            user = UserAccount(
                name=f"User {i}",
                email=f"user{i}@example.com",
                phone=f"98765432{i}",
                bio="This is a sample bio.",
                dob="1995-01-01",
                gender=random.choice(["Male", "Female", "Other"]),
                description="Some description about user",
                is_active=True,
                is_staff=False,
                is_blocked=False,
                password="testpassword123",  # Not hashed for dev
                privacy_policy_accepted=True,
                location=random.choice(["Kochi", "Trivandrum", "Delhi", "Mumbai"]),
                last_login_timestamp=timezone.now()
            )

            # ✅ Assign profile picture
            if profile_pics:
                random_pic = random.choice(profile_pics)
                pic_path = os.path.join(PROFILE_PIC_DIR, random_pic)
                with open(pic_path, 'rb') as img_file:
                    user.profilepicture.save(f"profile_{i}.jpg", File(img_file), save=False)

            user.save()

            # ✅ Assign random interests
            selected_interests = random.sample(interests, k=random.randint(3, 5))
            for interest in selected_interests:
                UserInterest.objects.create(userId=user, interestId=interest)
            
            selected_interests = random.sample(interests, k=random.randint(3, 5))
            for interest in selected_interests:
                InstantInterest.objects.create(user=user, interest=interest)

        self.stdout.write(self.style.SUCCESS('✅ 10 UserAccount users with random profile pictures and interests created!'))