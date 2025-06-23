#This is to authenticate the already existing JWT Tokens coming in for Socket creation requests.
# Also we will plug this custom class into DEFAULT_AUTHENTICATION_CLASSES, so that
import jwt #PyJWT library for decoding the JWT
from django.conf import settings #To get the shared secret from settings.
from django.contrib.auth.models import AnonymousUser,User
from rest_framework.authentication import BaseAuthentication #Base class for custom authentication
from rest_framework.exceptions import AuthenticationFailed #Used t throw 401
from .functions import get_user_details




class ExternalJWTAuthentication(BaseAuthentication):#custom class for authenticating jwt
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None #DRF will treat this as an anonyomus user.
        
        #1. Make sure prefix is bearer
        try:
            prefix,token = auth_header.split() #Bearer <token> format
            if prefix.lower()!='bearer':
                raise AuthenticationFailed('Authorization header must start with Bearer')
            
        except ValueError:
            raise AuthenticationFailed('Invalid Authorization header format')
        
        #2. Decode and verify the JWT using the secret key.
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                settings.ALGORITHM
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')
        
        #3. Extract user identity
        user_id = payload.get('user_id')
        if not user_id:
            raise AuthenticationFailed('Token payload missing user_id')
        
        # 4. Retrieve user from shared DB
        user_info = get_user_details(user_id)
        if not user_info:
            raise AuthenticationFailed('Unable to fetch user details from shared user DB')

        # 5. Create and return a pseudo user object
        user = type('RemoteUser', (), {
            'id': user_info.get('id'),
            'username': user_info.get('username'),
            'email': user_info.get('email'),
            'is_authenticated': True
        })()

        return (user,token)

# We must make sure the utility function returns a similar object.