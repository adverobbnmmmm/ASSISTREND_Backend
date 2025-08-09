from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Profile,Post
from ..serializers import PostSerializer

@api_view(['GET'])
def search_users(request):
    request_query = request.GET.get('q', '')
    
    if request_query:
        results = Profile.objects.filter(userName__icontains=request_query).values('id', 'userName', 'profileImageUrl')
    else:
        results = Profile.objects.none()
    formatted_results = [
        {'id': r['id'], 'name': r['userName'], 'profileImageUrl': r['profileImageUrl']} for r in results
    ]
    return Response({
        'count': len(formatted_results),
        'next': None,
        'previous': None,
        'results': formatted_results
    })

@api_view(['GET'])
def search_posts_by_caption(request):
    request_query = request.GET.get('q', '')
    if request_query:
        results = Post.objects.filter(caption__icontains=request_query)
    else:
        results = Post.objects.none()
    serializer = PostSerializer(results, many=True, context={'user_id': request.user.id})
    post=[serializer.data]
    return Response({'results':serializer.data})
