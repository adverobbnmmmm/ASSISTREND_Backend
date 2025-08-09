"""
ASGI config for message_service project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter,URLRouter
from django.core.asgi import get_asgi_application
from message.routing import websocket_urlpatterns #our websocket routes
from message.middleware import JWTAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'message_service.settings')

application = ProtocolTypeRouter({#tells how to route different type of connections
    "http":get_asgi_application(),
    "websocket":JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
})
