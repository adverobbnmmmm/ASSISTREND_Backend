from .models import UserProfile

def calculate_match_score(user1_profile, user2_profile):
    score = 0
    common_interests = set(user1_profile.interests.keys()) & set(user2_profile.interests.keys())
    score += len(common_interests) * 10
    return score

def find_matches(user, min_score=30, limit=10):
    user_profile = UserProfile.objects.get(user=user)
    potential_matches = UserProfile.objects.exclude(user=user)
    scored_matches = []
    

    for profile in potential_matches:
        score = calculate_match_score(user_profile, profile)
        if score >= min_score:
            scored_matches.append({
                'user_id': profile.user.id,
                'username': profile.user.username,
                'score': score,
                'online': profile.online_status
            })
    return sorted(scored_matches, key=lambda x: x['score'], reverse=True)[:limit]
