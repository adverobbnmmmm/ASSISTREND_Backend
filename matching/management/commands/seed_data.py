from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from matching.models import UserProfile
import random

User = get_user_model()

INTEREST_CATEGORIES = [
    "music", "sports", "movies", "books", "travel", "gaming", "cooking", "fitness"
]

def generate_random_interests():
    selected_keys = random.sample(INTEREST_CATEGORIES, k=random.randint(3, 5))
    return {key: "interested" for key in selected_keys}

class Command(BaseCommand):
    help = 'Seed dummy users and profiles with diverse interests'

    def handle(self, *args, **kwargs):
        UserProfile.objects.all().delete()
        User.objects.all().delete()

        for i in range(10):
            username = f'user{i}'
            email = f'user{i}@example.com'
            password = 'testpassword123'

            user = User.objects.create(username=username, email=email)
            user.set_password(password)
            user.save()

            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'online_status': random.choice([True, False]),
                    'interests': generate_random_interests(),
                    'preferences': {"dark_mode": random.choice([True, False])}
                }
            )

        self.stdout.write(self.style.SUCCESS('✅ 10 users with profiles created or updated!'))
