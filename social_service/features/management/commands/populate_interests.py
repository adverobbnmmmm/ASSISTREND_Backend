from django.core.management.base import BaseCommand
from features.models import Interest


class Command(BaseCommand):
    help = 'Populate the database with default interests'

    def handle(self, *args, **options):
        interests = [
            'Technology', 'Sports', 'Music', 'Movies', 'Books', 'Travel', 'Food', 
            'Art', 'Photography', 'Gaming', 'Fitness', 'Fashion', 'Science', 
            'Nature', 'Dancing', 'Cooking', 'Writing', 'Languages', 'History', 
            'Politics', 'Business', 'Health', 'Education', 'Entertainment', 
            'Lifestyle', 'DIY', 'Crafts', 'Gardening', 'Pets', 'Automotive',
            'Real Estate', 'Finance', 'Investing', 'Cryptocurrency', 'Yoga',
            'Meditation', 'Spirituality', 'Philosophy', 'Psychology', 'Sociology',
            'Volunteering', 'Charity', 'Environment', 'Sustainability', 'Activism'
        ]
        
        created_count = 0
        for interest_name in interests:
            interest, created = Interest.objects.get_or_create(
                interestName=interest_name
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created interest: {interest_name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} interests')
        )
