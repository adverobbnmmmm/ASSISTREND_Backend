from django.urls import path
from . import views
from .viewss import searchViews,likeViews,commentViews,searchNoElastic,profileViews

urlpatterns = [
    path('profile/', views.getProfile, name='get_profile'),
    path('getProfiles/', profileViews.getProfiles, name='get_profiles'),
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
    path('searchUsersE/',searchNoElastic.search_users, name='search_users_e'),
    path('searchPostE/',searchNoElastic.search_posts_by_caption, name='search_post_e'),
    path('addLike/', likeViews.addLike, name='add_like'),
    path('removeLike/', likeViews.removeLike, name='remove_like'),
    path('getComment/', commentViews.getComment, name='get_comment'),
    path('addComment/', commentViews.addComment, name='add_comment'),
    # Profile setup endpoints
    path('setup-profile/', views.setupProfile, name='setup_profile'),
    path('get-interests/', views.getInterests, name='get_interests'),
    path('check-profile/', views.checkProfileExists, name='check_profile'),
    path('user-profile/', views.getUserProfile, name='user_profile'),
    path('test-database/', views.testDatabase, name='test_database'),  # Add test endpoint
    path('checkServerStatus/', views.checkServerStatus, name='check_server_status'),  # New endpoint to check server status
]