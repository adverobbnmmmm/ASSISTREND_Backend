from django.urls import path
from .views import RequestSocketSession,GetMissedChats

urlpatterns = [
    path('api/socket-session',RequestSocketSession.as_view(),name='request_socket_session'),
    path('api/missed-messages/', GetMissedChats.as_view(), name='missed-messages'),
]