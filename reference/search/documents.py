# search/documents.py
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Post

@registry.register_document
class PostDocument(Document):
    Hashtags = fields.TextField(
    Analyzer='standard',
    Fields={
    'raw': fields.KeywordField(),
    }
    )

    Location = fields.TextField(
    Analyzer='standard',
    Fields={
    'raw': fields.KeywordField(),
    }
    )

class Index:
    Name = 'posts'
    Settings = {
    'number_of_shards': 1,
    'number_of_replicas': 0
    }

class Django:
    Model = Post
    Fields = [
    'id',
    'title',
    'content',
    'created_at',
    'updated_at',
    ]