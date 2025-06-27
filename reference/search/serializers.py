from rest_framework import serializers
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from .models import Post
from .documents import PostDocument
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        Model = Post
        Fields = '__all__'


class PostDocumentSerializer(DocumentSerializer):
    class Meta:
        Document = PostDocument
        Fields = [
            'id',
            'title',
            'content',
            'hashtags',
            'location',
            'created_at',
            'updated_at',
        ]