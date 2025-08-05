from django.core.management.base import BaseCommand
from connect_app.models import UserAccount, Interest, UserInterest
import random
from django.utils import timezone

INTEREST_CATEGORIES = [
    "music", "sports", "movies", "books", "travel", "gaming", "cooking", "fitness"
]

class Command(BaseCommand):
    help = 'Seed dummy UserAccount users with interests'

    def handle(self, *args, **kwargs):
        # Clear existing data
        UserInterest.objects.all().delete()
        Interest.objects.all().delete()
        UserAccount.objects.all().delete()

        # Create Interest objects
        interests = []
        for interest_name in INTEREST_CATEGORIES:
            interest = Interest.objects.create(interestName=interest_name)
            interests.append(interest)

        # Create dummy users and assign random interests
        for i in range(10):
            user = UserAccount.objects.create(
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
                password="testpassword123",  # You can hash it later if needed
                privacy_policy_accepted=True,
                location=random.choice(["Kochi", "Trivandrum", "Delhi", "Mumbai"]),
                last_login_timestamp=timezone.now()
            )

            # Assign 3-5 random interests
            selected_interests = random.sample(interests, k=random.randint(3, 5))
            for interest in selected_interests:
                UserInterest.objects.create(userId=user, interestId=interest)

        self.stdout.write(self.style.SUCCESS('✅ 10 UserAccount users with interests created!'))
