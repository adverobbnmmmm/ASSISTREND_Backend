from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_elasticsearch_dsl_drf.filter_backends import (
FilteringFilterBackend,
SearchFilterBackend,
OrderingFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from .models import Post
from .documents import PostDocument
from .serializers import PostSerializer, PostDocumentSerializer
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q
from django.conf import settings
import elasticsearch
class PostViewSet(viewsets.ModelViewSet):
    Queryset = Post.objects.all()
    Serializer_class = PostSerializer
    
class PostDocumentViewSet(DocumentViewSet):
    Document = PostDocument
    Serializer_class = PostDocumentSerializer
    Filter_backends = [
    FilteringFilterBackend,
    SearchFilterBackend,
    OrderingFilterBackend,
    ]
    Search_fields = (
    'title',
    'content',
    'hashtags',
    'location',
    )
    Filter_fields = {
    'hashtags': 'hashtags.raw',
    'location': 'location.raw',
    }
    Ordering_fields = {
    'created_at': 'created_at',
    }
    Ordering = ('-created_at',)
    
@action(detail=False, methods=['get'])
def trending_hashtags(self, request):
"""
Get trending hashtags based on frequency in posts
"""
    Client = elasticsearch.Elasticsearch(settings.ELASTICSEARCH_DSL['default']['hosts'])
    # Aggregate hashtags
    S = Search(using=client, index='posts')
    s.aggs.bucket('hashtag_terms', 'terms', field='hashtags.raw', size=10)
    response = s.execute()
    # Extract trending hashtags
    Trending = [
    {
    'hashtag': bucket.key,
    'count': bucket.doc_count
    }
    For bucket in response.aggregations.hashtag_terms.buckets
    ]
    Return Response(trending)