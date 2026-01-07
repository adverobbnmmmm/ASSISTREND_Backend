from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..documents import UserDocument, PostDocument

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

@api_view(['GET'])
def search_posts_by_caption(request):
    query = request.GET.get('q', '')
    # Use fuzzy matching and autocomplete (edge_ngram) for captions and category name
    search = PostDocument.search()
    # Autocomplete suggestion
    suggest = search.suggest(
        'caption_suggest',
        query,
        completion={
            'field': 'caption.suggest',
            'fuzzy': {
                'fuzziness': 2
            }
        }
    )
    # Fuzzy + autocomplete match on both caption and category.name
    results = search.query(
        "multi_match",
        query=query,
        fields=["caption", "category.name"],
        fuzziness="auto",
        type="bool_prefix"
    )
    posts = [
        {
            'id': hit.id,
            'caption': hit.caption,
            'image_url': hit.image_url,
            'created_at': hit.created_at,
            'user': getattr(hit, 'user', None),
            'category': getattr(hit, 'category', None)
        }
        for hit in results
    ]
    # Get autocomplete suggestions
    suggestions = []
    if hasattr(suggest, 'to_dict'):
        suggest_dict = suggest.to_dict()
        for option in suggest_dict.get('caption_suggest', [{}])[0].get('options', []):
            suggestions.append(option.get('text'))
    return Response({'results': posts, 'suggestions': suggestions})