from django.urls import path
from . import views
from .viewss import searchViews,likeViews,commentViews

urlpatterns = [
    path('profile/', views.getProfile, name='get_profile'),
    path('update-about/', views.updateAbout, name='update_about'),
    path('update-emoji/', views.updateEmoji, name='update_emoji'),
    path('update-name/', views.updateName, name='update_name'),
    path('update-socials/', views.updateSocials, name='update_socials'),
    path('update-interests/', views.updateInterests, name='update_interests'),
    path('uploadPost/',views.uploadPost,name='uploadPost'),
    path('getPostById/<str:username>/', views.getPostById, name='getPostById'),
    path('getPostUserFeed/',views.getPostUserFeed,name='getPostUserFeed'),
    path('search/users/', searchViews.search_users, name='search_users'),
    path('search/posts/', searchViews.search_posts_by_caption, name='search_posts_by_caption'),
    path('addLike/', likeViews.addLike, name='add_like'),
    path('removeLike/', likeViews.removeLike, name='remove_like'),
    path('getComment',commentViews.getComment, name='get_comment'),
    path('addComment',commentViews.addComment, name='add_comment'),
]