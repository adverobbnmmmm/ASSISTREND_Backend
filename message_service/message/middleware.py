# message/middleware.py

import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from message.models import UserAccount
from urllib.parse import parse_qs


class JWTAuthMiddleware:
    """ASGI middleware for JWT authentication"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        scope["user"] = AnonymousUser()
        print("🔐 [JWT Middleware] Scope received")

        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        if token:
            try:
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM]
                )
                user_id = payload.get("user_id")
                if user_id:
                    user = await self.get_user(user_id)
                    scope["user"] = user
            except Exception as e:
                print(f"❌ JWT decode failed: {e}")

        return await self.app(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return UserAccount.objects.get(id=user_id)
        except UserAccount.DoesNotExist:
            return AnonymousUser()
