from django.urls import path
from .views import RequestSocketSession

urlpatterns = [
    path('api/socket-session',RequestSocketSession.as_view(),name='request_socket_session'),
]