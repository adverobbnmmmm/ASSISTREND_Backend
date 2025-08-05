
from .models import UserAccount, UserInterest, Interest
def calculate_match_score(user1, user2):
    user1_interests = set(UserInterest.objects.filter(userId=user1).values_list('interestId', flat=True))
    user2_interests = set(UserInterest.objects.filter(userId=user2).values_list('interestId', flat=True))
    common = user1_interests.intersection(user2_interests)
    return len(common) * 10  # 10 points per shared interest


def get_user_hobbies(user):
    # Fetch all interest names for the given user
    return list(
        UserInterest.objects.filter(userId=user)
        .select_related('interestId')
        .values_list('interestId__interestName', flat=True)
    )

#Find matching profiles and returns the user details
def find_matches(user, min_score=10, limit=5):
    others = UserAccount.objects.exclude(id=user.id)
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
                'hobbies': get_user_hobbies(other) 
            })

    return sorted(matches, key=lambda x: x['score'], reverse=True)[:limit]
