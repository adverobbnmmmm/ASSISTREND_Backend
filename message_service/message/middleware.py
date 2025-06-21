#middleware to authenticat the websocketsessiontoken coming in.

from urllib.parse import parse_qs  # Used to extract the token from the WebSocket URL query string
from django.core.cache import cache  # To validate the short-lived session token from the cache
from channels.db import database_sync_to_async  # Allows DB access inside async functions
from django.contrib.auth.models import AnonymousUser  # Default fallback user
from message.models import UserAccount  # Shared user model (linked via managed=False in our microservice)
import logging  # For debugging/visibility

# Set up logging
logger = logging.getLogger("django")


class WebSocketSessionTokenAuthMiddleware:
    """
    This is the outer middleware class. It wraps the ASGI app and spawns a middleware instance per WebSocket connection.
    """

    def __init__(self, inner):
        # `inner` is the next ASGI layer (usually a URLRouter).
        self.inner = inner

    def __call__(self, scope):
        # This is called once per incoming WebSocket connection.
        # It creates a middleware instance for that specific connection.
        return WebSocketSessionTokenAuthMiddlewareInstance(scope, self.inner)


class WebSocketSessionTokenAuthMiddlewareInstance:
    """
    Handles a single WebSocket connection.
    Responsible for extracting and validating the session token and attaching the user to the scope.
    """

    def __init__(self, scope, inner):
        self.scope = scope  # Contains connection metadata, like headers, query string, etc.
        self.inner = inner  # The next layer to call once authenticated (typically a consumer)

    async def __call__(self, receive, send):
        """
        The core function that gets triggered when a WebSocket connection is opened.
        It handles token extraction, cache validation, user lookup, and attaching the user to scope.
        """

        try:
            # Step 1: Extract the query string from the WebSocket request (e.g., "?token=abc123")
            query_string = self.scope.get("query_string", b"").decode()
            query_params = parse_qs(query_string)

            # Step 2: Get the token value (list) from the query parameters
            token_list = query_params.get("token", [])

            # Default the user to AnonymousUser (unauthenticated)
            user = AnonymousUser()

            # Step 3: Check if token was sent at all
            if not token_list:
                logger.warning("Missing WebSocket session token in query string.")
                await self._reject_connection(send, code=4401, reason="Token missing")
                return  # End the connection early

            # Step 4: Extract token string 
            token = token_list[0]

            # Step 5: Use the token to look up the user ID in Django's cache
            user_id = cache.get(f"ws_session_{token}")

            if not user_id:
                # If not found in cache (expired or tampered), reject the connection
                logger.warning(f"Invalid or expired WebSocket token: {token}")
                await self._reject_connection(send, code=4402, reason="Token invalid or expired")
                return

            # Step 6: Now try to fetch the actual user from the database using the user ID
            user = await self.get_user(user_id)

            if isinstance(user, AnonymousUser):
                # If user doesn't exist in the DB, reject
                logger.warning(f"No user found with ID: {user_id}")
                await self._reject_connection(send, code=4403, reason="User not found")
                return

            # Step 7: Attach the user object to the scope so that your consumers can access it
            self.scope["user"] = user

            # Step 8: Now authentication is complete — pass control to the inner ASGI app (consumer)
            return await self.inner(self.scope, receive, send)

        except Exception as e:
            # Catch-all in case anything breaks
            logger.exception("Error during WebSocket authentication.")
            await self._reject_connection(send, code=4500, reason="Internal server error")

    @database_sync_to_async
    def get_user(self, user_id):
        """
        Looks up a user in the shared UserAccount table using their ID.
        This is done using Django ORM, but made async-safe with database_sync_to_async.
        """
        try:
            return UserAccount.objects.get(id=user_id)
        except UserAccount.DoesNotExist:
            return AnonymousUser()

    async def _reject_connection(self, send, code, reason="Unauthorized"):
        """
        Helper function to close a WebSocket connection with a specific error code and reason.
        This gives the client feedback on why they were disconnected.
        """
        await send({
            "type": "websocket.close",
            "code": code,
            "reason": reason
        })
