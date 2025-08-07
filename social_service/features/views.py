from django.shortcuts import render
from django.http import JsonResponse

from .serializers import PostSerializer, ProfileSetupSerializer, InterestSerializer, ProfileSerializer
from .models import *  # Import all models from the same app
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .documents import UserDocument, PostDocument
# Create your views here.
def getProfile(request):
    """
    View to get the profile of a user.
    This function will handle the logic to retrieve and display user profile information.
    """
    userId = request.GET.get('userId')
    user = UserAccount.objects.get(id=userId)
    name = user.name
    
    # Get profile data
    try:
        profile = Profile.objects.get(userId=user)
        username = profile.userName  
        emoji = profile.emoji
        about = profile.about
        points = profile.points
    except Profile.DoesNotExist:
        username = ""
        emoji = ""
        about = ""
        points = 0
        
    badges = list(UserBadge.objects.filter(user=user).values('badge__name', 'badge__image'))
    posts = list(Post.objects.filter(user=user).values('id', 'caption', 'image_url', 'created_at'))
    stories = list(Story.objects.filter(user=user).values('id', 'content', 'created_at'))
    liked_posts = list(PostLike.objects.filter(user=user).values('post_id'))
    tagged_posts = list(TaggedPerson.objects.filter(user=user).values('post_id')) 
    socials = list(SocialLink.objects.filter(user=user).values('platform', 'url'))
    interests = list(UserInterest.objects.filter(userId=user).select_related('interestId').values('interestId__interestName'))
    
    return JsonResponse({
        'name': name,
        'username': username,
        'emoji': emoji,
        'about': about,
        'interests': interests,
        'badges': badges,
        'points': points,
        'posts': posts,
        'stories': stories,
        'likedPosts': liked_posts,
        'taggedPosts': tagged_posts,
        'socials': socials
    })
    
@api_view(['POST'])
def updateAbout(request):
    """
    View to update the 'about' section of a user's profile.
    This function will handle the logic to update the 'about' field in the Profile model.
    """
    userId = request.data.get('userId')
    about = request.data.get('about')
    
    try:
        user = UserAccount.objects.get(id=userId)
        profile, created = Profile.objects.get_or_create(userId=user)
        profile.about = about
        profile.save()
        return JsonResponse({'status': 'success', 'message': 'About section updated successfully.'})
    except UserAccount.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

@api_view(['POST'])
def updateName(request):
    """
    View to update the name of a user.
    This function will handle the logic to update the 'name' field in the UserAccount model.
    """
    userId = request.data.get('userId')
    name = request.data.get('name')
    
    try:
        user = UserAccount.objects.get(id=userId)
        user.name = name
        user.save()
        return JsonResponse({'status': 'success', 'message': 'Name updated successfully.'})
    except UserAccount.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

@api_view(['POST'])
def updateEmoji(request):
    """
    View to update the emoji of a user's profile.
    This function will handle the logic to update the 'emoji' field in the Profile model.
    """
    userId = request.data.get('userId')
    emoji = request.data.get('emoji')
    
    try:
        user = UserAccount.objects.get(id=userId)
        profile, created = Profile.objects.get_or_create(userId=user)
        profile.emoji = emoji
        profile.save()
        return JsonResponse({'status': 'success', 'message': 'Emoji updated successfully.'})
    except UserAccount.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

@api_view(['POST'])
def updateSocials(request):
    """
    View to update the social links of a user's profile.
    This function will handle the logic to update the social links in the SocialLink model.
    """
    userId = request.data.get('userId')
    platform = request.data.get('platform')
    url = request.data.get('url')
    
    try:
        user = UserAccount.objects.get(id=userId)
        social_link, created = SocialLink.objects.get_or_create(user=user, platform=platform)
        social_link.url = url
        social_link.save()
        return JsonResponse({'status': 'success', 'message': 'Social link updated successfully.'})
    except UserAccount.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

@api_view(['POST'])
def updateInterests(request):
    """
    View to update the interests of a user.
    This function will handle the logic to update the interests in the UserInterest model.
    """
    userId = request.data.get('userId')
    interestNames = request.data.getlist('interests')  # Expecting a list of interest names
    
    try:
        user = UserAccount.objects.get(id=userId)
        UserInterest.objects.filter(userId=user).delete()  # Clear existing interests
        
        for interestName in interestNames:
            interest, created = Interest.objects.get_or_create(interestName=interestName)
            UserInterest.objects.create(userId=user, interestId=interest)
        
        return JsonResponse({'status': 'success', 'message': 'Interests updated successfully.'})
    except UserAccount.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
    

@api_view(['POST'])
def uploadPost(request):
    """
    View to upload a post.
    This function will handle the logic to upload a post to the Post model.
    """
    print(request.data)
    userId = request.data.get('userId')
    caption = request.data.get('caption')
    imageUrl = request.data.get('imageUrl')  # Expecting an image URL
    audioUrl = request.data.get('audioUrl') # Expecting an audio URL
    category=request.data.get('category')
    taggedUsers=request.data.get('taggedUserIds', [])  # Expecting a list of tagged user IDs
    # print(f"Tagged Users: {taggedUsers}")
    try:
        user = UserAccount.objects.get(id=userId)
    except UserAccount.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
  
    try:
        categoryId=PostCategory.objects.get(name=category).id
    except PostCategory.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Category not found.'}, status=404)
  
    try:
        post = Post.objects.create(
            user=user,
            caption=caption,
            image_url=imageUrl,
            audio_url=audioUrl,
            category_id=categoryId
        )
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    try:
        for taggedUserId in taggedUsers:
            tagged_user = UserAccount.objects.get(id=taggedUserId)
            TaggedPerson.objects.create(user=tagged_user, post=post)
    except UserAccount.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Tagged user not found.'}, status=404)
    return JsonResponse({'status': 'success', 'message': 'Post uploaded successfully.'})

def getPostById(request, username):
    
    try:
        userId=Profile.objects.get(userName=username).userId_id
    except Profile.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
    
    posts = list(Post.objects.filter(user=userId).values('id', 'caption', 'image_url', 'audio_url', 'created_at'))
    if not posts:
        return JsonResponse({'status': 'error', 'message': 'Posts not found.'}, status=404)
    
    return JsonResponse({'status': 'success', 'message': 'Posts found.', 'posts': posts})


@api_view(['GET'])
def getPostUserFeed(request):   
    post=Post.objects.all().order_by('-created_at')
    serializer=PostSerializer(post,many=True,context={'user_id': request.GET.get('userId')})
    return Response(serializer.data)

@api_view(['GET'])
def search_users(request):
    query = request.GET.get('q', '')

    search = UserDocument.search()
    # Autocomplete suggestion
    suggest = search.suggest(
        'user_suggest',
        query,  
        completion={
            'field': 'name.suggest',
            'fuzzy': {
                'fuzziness': 2
            }
        }
    )
    # Fuzzy + autocomplete match
    results = search.query(
        "multi_match",
        query=query,
        fields=['name', 'email'],
        fuzziness="auto",
        type="bool_prefix"
    )
    users = [{'id': hit.id, 'name': hit.name, 'email': hit.email} for hit in results]
    # Get autocomplete suggestions
    suggestions = []
    if hasattr(suggest, 'to_dict'):
        suggest_dict = suggest.to_dict()
        for option in suggest_dict.get('user_suggest', [{}])[0].get('options', []):
            suggestions.append(option.get('text'))
    return Response({'results': users, 'suggestions': suggestions})


@api_view(['POST'])
@api_view(['POST'])
def setupProfile(request):
    """
    View to setup user profile after OTP verification.
    This function will handle the logic to create a profile for the user.
    """
    print(f'DEBUG: setupProfile called with data: {request.data}')
    
    try:
        user_id = request.data.get('userId')
        print(f'DEBUG: Extracted userId: {user_id}')
        
        if not user_id:
            print('DEBUG: No userId provided')
            return Response({'status': 'error', 'message': 'User ID is required.'}, status=400)
        
        user = UserAccount.objects.get(id=user_id)
        print(f'DEBUG: Found user: {user.email}')
        
        # Check if profile already exists
        if Profile.objects.filter(userId=user).exists():
            print('DEBUG: Profile already exists')
            return Response({'status': 'error', 'message': 'Profile already exists.'}, status=400)
        
        print('DEBUG: Creating serializer with context')
        serializer = ProfileSetupSerializer(data=request.data, context={'user': user})
        
        if serializer.is_valid():
            print('DEBUG: Serializer is valid, saving profile')
            profile = serializer.save()
            print(f'DEBUG: Profile saved successfully: {profile.id}')
            return Response({'status': 'success', 'message': 'Profile setup completed successfully.'})
        else:
            print(f'DEBUG: Serializer errors: {serializer.errors}')
            return Response({'status': 'error', 'message': 'Invalid data', 'errors': serializer.errors}, status=400)
    
    except UserAccount.DoesNotExist:
        print(f'DEBUG: UserAccount with id {user_id} not found')
        return Response({'status': 'error', 'message': 'User not found.'}, status=404)
    except Exception as e:
        print(f'DEBUG: Exception in setupProfile: {str(e)}')
        return Response({'status': 'error', 'message': str(e)}, status=500)


@api_view(['GET'])
def getInterests(request):
    """
    View to get all available interests.
    This function will return all interests that users can select from.
    """
    interests = Interest.objects.all()
    serializer = InterestSerializer(interests, many=True)
    return Response({'status': 'success', 'interests': serializer.data})


@api_view(['GET'])
def checkProfileExists(request):
    """
    View to check if a user's profile exists.
    This function will check if the user has completed profile setup.
    """
    user_id = request.GET.get('userId')
    print(f'DEBUG: checkProfileExists called with userId: {user_id}')
    
    if not user_id:
        print('DEBUG: No userId provided')
        return Response({'status': 'error', 'message': 'User ID is required.'}, status=400)
    
    try:
        # Get the UserAccount object first
        user = UserAccount.objects.get(id=user_id)
        print(f'DEBUG: Found user: {user.email}')
        
        # Check if a Profile exists for this UserAccount
        profile_exists = Profile.objects.filter(userId=user).exists()
        print(f'DEBUG: Profile exists: {profile_exists}')
        
        return Response({'status': 'success', 'profileExists': profile_exists})
    except UserAccount.DoesNotExist:
        print(f'DEBUG: UserAccount with id {user_id} not found')
        return Response({'status': 'error', 'message': 'User not found.'}, status=404)


@api_view(['GET'])
def getUserProfile(request):
    """
    View to get user profile data.
    This function will return the user's profile information.
    """
    user_id = request.GET.get('userId')
    if not user_id:
        return Response({'status': 'error', 'message': 'User ID is required.'}, status=400)
    
    try:
        user = UserAccount.objects.get(id=user_id)
        profile = Profile.objects.get(userId=user)
        serializer = ProfileSerializer(profile)
        return Response({'status': 'success', 'profile': serializer.data})
    except UserAccount.DoesNotExist:
        return Response({'status': 'error', 'message': 'User not found.'}, status=404)
    except Profile.DoesNotExist:
        return Response({'status': 'error', 'message': 'Profile not found.'}, status=404)

@api_view(['GET'])
def testDatabase(request):
    """
    Test endpoint to check database connectivity and table structure
    """
    try:
        # Test UserAccount table
        user_count = UserAccount.objects.count()
        print(f'DEBUG: UserAccount table has {user_count} records')
        
        # Test Profile table
        profile_count = Profile.objects.count()
        print(f'DEBUG: Profile table has {profile_count} records')
        
        # Test Interest table
        interest_count = Interest.objects.count()
        print(f'DEBUG: Interest table has {interest_count} records')
        
        return Response({
            'status': 'success',
            'message': 'Database connection successful',
            'counts': {
                'users': user_count,
                'profiles': profile_count,
                'interests': interest_count
            }
        })
    except Exception as e:
        print(f'DEBUG: Database test error: {str(e)}')
        return Response({
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }, status=500)

@api_view(['GET'])
def checkServerStatus(request):
    """
    Endpoint to check if the server is running and responding.
    """
    return Response({'status': 'success', 'message': 'Server is running.'})


