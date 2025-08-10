from .models import UserAccount, UserInterest, Interest, InstantInterest
from django.db.models import Max

def calculate_match_score(user_one, user_two):
    # Get latest instant interests for user_one
    latest_time = InstantInterest.objects.filter(user=user_one).aggregate(
        Max('created_at')
    )['created_at__max']

    latest_user_instant_ids = set()
    if latest_time:
        latest_user_instant_ids = set(
            InstantInterest.objects.filter(user=user_one, created_at=latest_time)
            .values_list('interest_id', flat=True)
        )

    # Permanent interests for user_one
    user_one_permanent_ids = set(
        UserInterest.objects.filter(userId=user_one)
        .values_list('interestId', flat=True)
    )

    # Combine for user_one
    user_one_all_interests = user_one_permanent_ids.union(latest_user_instant_ids)

    # Permanent + instant interests for user_two
    user_two_permanent_ids = set(
        UserInterest.objects.filter(userId=user_two)
        .values_list('interestId', flat=True)
    )
    user_two_instant_ids = set(
        InstantInterest.objects.filter(user=user_two)
        .values_list('interest_id', flat=True)
    )
    user_two_all_interests = user_two_permanent_ids.union(user_two_instant_ids)

    # Calculate common interests
    common = user_one_all_interests.intersection(user_two_all_interests)
    return len(common) * 10  # 10 points per shared interest


def get_user_hobbies(user):
    """Fetch all permanent and instant interest names for the given user."""

    # Permanent interests
    permanent_interests = UserInterest.objects.filter(userId=user) \
        .select_related('interestId') \
        .values_list('interestId__interestName', flat=True)

    # Instant interests
    instant_interests = InstantInterest.objects.filter(user=user) \
        .select_related('interest') \
        .values_list('interest__interestName', flat=True)

     # Combine and remove duplicates using set
    all_interests = set(permanent_interests) | set(instant_interests)
    
    return list(all_interests)



def find_matches(user, min_score=10, limit=5):
    """Find matching profiles and return details."""
    others = UserAccount.objects.filter(is_active=True).exclude(id=user.id)
    matches = []
    for other in others:
        score = calculate_match_score(user, other)
        if score >= min_score:
            matches.append({
                'user_id': other.id,
                'phone': other.phone,
                'profilepicture': other.profilepicture,
                'name': other.name,
                'score': score,
                'interests': get_user_hobbies(other)
            })

    return sorted(matches, key=lambda x: x['score'], reverse=True)[:limit]
