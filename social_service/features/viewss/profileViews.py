from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Profile
from ..serializers import ProfileSerializer

@api_view(['GET'])
def getProfiles(request):
    """
    Endpoint to retrieve the user profile based on the username.
    """
    username = request.GET.get('username')
    if not username:
        return Response({'error': 'Username parameter is required.'}, status=400)
    try:
        profile = Profile.objects.get(userName=username)
        serializer = ProfileSerializer(profile, context={'user_id': request.user.id})
        return Response(serializer.data)
    except Profile.DoesNotExist:
        return Response({'error': 'Profile not found.'}, status=404)