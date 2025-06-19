from django.shortcuts import render
from django.http import JsonResponse
from .models import *  # Import all models from the same app

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
    
    return JsonResponse({
        'name': name,
        'username': username,
        'emoji': emoji,
        'about': about,
        'badges': badges,
        'points': points,
        'posts': posts,
        'stories': stories,
        'likedPosts': liked_posts,
        'taggedPosts': tagged_posts,
        'socials': socials
    })
    
    