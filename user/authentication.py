from datetime import datetime, timedelta

import jwt
from rest_framework import status

from user.exceptions import AuthenticationError
from achare.settings import ACCESS_TOKEN_EXP, REFRESH_TOKEN_EXP, SECRET_KEY
from user.models import User


def check_user_exists(user_id: str) -> bool:
    return User.objects.filter(id=user_id).exists()


def get_user_obj(user_id: str) -> User:
    return User.objects.filter(pk=user_id).first()


def jwt_encode(payload):
    """
    document:
        https://pyjwt.readthedocs.io/en/latest/
    """
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def jwt_decode(token):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])


def generate_refresh_token(user_id):
    payload = {
        "uid": user_id,
        "type": "refresh_token",
        "role": "user",
        "exp": datetime.now() + timedelta(**REFRESH_TOKEN_EXP),
    }
    return jwt_encode(payload)


def get_user_login_info(user_id: str) -> dict:
    return {
        "access_token": generate_access_token(user_id),
        "refresh_token": generate_refresh_token(user_id),
    }


class TokenValidator:
    token_type = None

    def get_token_payload(self, token):
        if token:
            try:
                return jwt_decode(token)
            except Exception:
                pass
                # logger.error(f"{type(error)}: {str(error)}")
        raise AuthenticationError

    def check_token_type(self, payload):
        token_type = payload.get("type")
        if token_type and token_type == self.token_type:
            return
        raise AuthenticationError

    def get_user_id_from_payload(self, payload):
        user_id = payload.get("uid")
        if user_id and check_user_exists(user_id):
            return user_id
        raise AuthenticationError

    def get_user_obj(self, payload):
        user_id = payload.get("uid")
        if user_id:
            user = get_user_obj(user_id)
            if user:
                return user
        raise AuthenticationError


def generate_access_token(user_id):
    payload = {
        "uid": user_id,
        "type": "access_token",
        "role": "user",
        "exp": datetime.now() + timedelta(**ACCESS_TOKEN_EXP),
    }
    return jwt_encode(payload)


class CustomResponseError(Exception):
    pass


class JWTAuthentication(TokenValidator):
    token_type = "access_token"

    def authenticate(self, request):
        try:
            access_token = request.META.get("HTTP_AUTHORIZATION")
            if access_token is None:
                access_token = request.POST.get(
                    "jwtToken", request.session.get("jwtToken")
                )
            token_payload = self.get_token_payload(access_token)
            self.check_token_type(token_payload)
            if token_payload.get("role") == "user":
                return self.get_user_obj(token_payload), access_token
            else:
                raise CustomResponseError(
                    "Authorization is not valid for this request",
                    status.HTTP_401_UNAUTHORIZED,
                )
        except Exception:
            raise AuthenticationError
