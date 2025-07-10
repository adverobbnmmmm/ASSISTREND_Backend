from rest_framework.decorators import api_view
from ..models import PostComment,Post,UserAccount
from django.http import JsonResponse

@api_view(['POST'])
def addComment(request):
    """
    View to add Commment to post. Send in PostId, Commenting userId
    """
    
    postId=request.data.get('postId')
    userId=request.data.get('userId')
    comment=request.data.get('comment')
    
    try:
        post = Post.objects.get(id=postId)
    except Post.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Post not found.'},status=404)
    
    try:
        user=UserAccount.objects.get(id=userId)
    except UserAccount.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
    
    try:
        PostComment.objects.create(
            post=post,
            user=user,
            comment=comment
        )
    except Exception as e:
         return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
     
    
    return JsonResponse({'status': 'success', 'message': 'Comment uploaded successfully.'})


def getComment(request):
    """
    View to get Comments for a post. Pass in the postID
    
    """

    postId=request.GET.get('postId')
    
    postComment=PostComment.objects.filter(post_id=postId)
    
    return JsonResponse({
        'status': 'success',
        'message': 'Comments found.',
        'comments': list(postComment.values('id', 'user_id', 'comment', 'created_at'))
    })

    
    
    