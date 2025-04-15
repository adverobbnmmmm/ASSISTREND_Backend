import requests

def get_user_details(user_id):
    try:
        response = requests.get(f"http://accounts-service:8001/api/users/{user_id}/")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Failed to fetch user details: {e}")
    return None