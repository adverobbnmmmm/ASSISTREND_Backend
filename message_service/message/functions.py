
from .models import UserAccount 

def get_user_details(user_id):
    try:
        user = UserAccount.objects.get(id=user_id)
        return {
            'id': user.id,
            'username': user.name,
            'email': user.email,
        }
    except UserAccount.DoesNotExist:
        return None
