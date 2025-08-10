from django.core.management.base import BaseCommand
from features.models import Interest


class Command(BaseCommand):
    help = 'Populate the database with default interests'

    def handle(self, *args, **options):
        # Curated list of 30 popular interests
        interests = [
            'Technology', 'Sports', 'Music', 'Movies', 'Books', 
            'Travel', 'Food', 'Art', 'Photography', 'Gaming',
            'Fitness', 'Fashion', 'Science', 'Nature', 'Dancing',
            'Cooking', 'Writing', 'Languages', 'Business', 'Health',
            'Education', 'Entertainment', 'DIY', 'Gardening', 'Pets',
            'Finance', 'Yoga', 'Meditation', 'Environment', 'Volunteering'
        ]
        
        # First, let's see what already exists
        existing_interests = set(Interest.objects.values_list('interestName', flat=True))
        self.stdout.write(f'Found {len(existing_interests)} existing interests: {existing_interests}')
        
        created_count = 0
        updated_count = 0
        
        for interest_name in interests:
            try:
                interest, created = Interest.objects.get_or_create(
                    interestName=interest_name
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'Created interest: {interest_name}')
                else:
                    updated_count += 1
                    self.stdout.write(f'Interest already exists: {interest_name}')
            except Exception as e:
                self.stdout.write(f'Error with interest {interest_name}: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(interests)} interests. '
                f'Created: {created_count}, Already existed: {updated_count}'
            )
        )
