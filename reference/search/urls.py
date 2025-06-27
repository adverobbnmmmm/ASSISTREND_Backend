from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, PostDocumentViewSet
Router = DefaultRouter()
Router.register(r'posts', PostViewSet)
Router.register(r'search', PostDocumentViewSet, basename='post-search')
Urlpatterns = [
    Path('', include(router.urls)),
]