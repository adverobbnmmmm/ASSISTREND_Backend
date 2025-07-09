from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from .models import UserAccount, Post, PostCategory

user_index = Index('users')
post_index = Index('posts')

@registry.register_document
class UserDocument(Document):
    name = fields.TextField(
        fields={
            'suggest': fields.CompletionField(),
        }
    )
    class Index:
        name = 'users'
    class Django:
        model = UserAccount
        fields = [
            'id',
            'email',
        ]

@registry.register_document
class PostDocument(Document):
    caption = fields.TextField(
        fields={
            'suggest': fields.CompletionField(),
        }
    )
    class Index:
        name = 'posts'
    class Django:
        model = Post
        fields = [
            'id',
            'image_url',
            'created_at',
        ]
        related_models = [UserAccount,PostCategory]

    user = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
    })
    
    category = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
    })
