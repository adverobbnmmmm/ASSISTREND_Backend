from django.shortcuts import render
from django.http import JsonResponse

from .serializers import PostSerializer
from .models import *  # Import all models from the same app
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
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
    category=request.data.get('category')
    try:
        user = UserAccount.objects.get(id=userId)
    except UserAccount.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
  
    try:
        categoryId=PostCategory.objects.get(name=category).id
    except Category.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Category not found.'}, status=404)
    
    try:
        post = Post.objects.create(
            user=user,
            caption=caption,
            image_url=imageUrl,
            category_id=categoryId
        )
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'success', 'message': 'Post uploaded successfully.'})

def getPostById(request, username):
    
    try:
        userId=Profile.objects.get(userName=username).userId_id
    except Profile.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
    
    posts = list(Post.objects.filter(user=userId).values('id', 'caption', 'image_url', 'created_at'))
    if not posts:
        return JsonResponse({'status': 'error', 'message': 'Posts not found.'}, status=404)
    
    return JsonResponse({'status': 'success', 'message': 'Posts found.', 'posts': posts})


@api_view(['GET'])
def getPostUserFeed(request):
    post=Post.objects.all().order_by('-created_at')
    serializer=PostSerializer(post,many=True)
    return Response(serializer.data)
    
    
    