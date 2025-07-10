from ..models import * 
from django.http import JsonResponse

def addLike(request):
    """
    View to add a like to a post.
    This function will handle the logic to add a like to the PostLike model.
    Prevents duplicate likes by the same user for the same post.
    """
    userId = request.GET.get('userId')
    postId = request.GET.get('postId')
    
    try:
        user = UserAccount.objects.get(id=userId)
        post = Post.objects.get(id=postId)
        like, created = PostLike.objects.get_or_create(user=user, post=post)
        if created:
            return JsonResponse({'status': 'success', 'message': 'Post liked successfully.'})
        else:
            return JsonResponse({'status': 'exists', 'message': 'User has already liked this post.'})
    except UserAccount.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
    except Post.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Post not found.'}, status=404)
    
def removeLike(request):
    
    """
    View to remove a like from a post.
    This function will handle the logic to remove a like from the PostLike model.
    """
    userId = request.data.get('userId')
    postId = request.data.get('postId')
    
    try:
        user = UserAccount.objects.get(id=userId)
        post = Post.objects.get(id=postId)
        PostLike.objects.filter(user=user, post=post).delete()
        return JsonResponse({'status': 'success', 'message': 'Post unliked successfully.'})
    except UserAccount.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
    except Post.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Post not found.'}, status=404)