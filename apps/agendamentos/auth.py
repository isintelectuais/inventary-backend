from ninja.security import APIKeyHeader
from ninja import NinjaAPI
from jose import JWTError, jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from typing import Optional

User = get_user_model()


class JWTAuth(APIKeyHeader):
    param_name = "Authorization"

    def authenticate(self, request, key):
        try:
            # Remove o prefixo "Bearer " se presente
            if key.startswith("Bearer "):
                key = key[7:]

            # Decodifica o token JWT
            payload = jwt.decode(
                key,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )

            # Obtém o usuário do payload
            user_id = payload.get("user_id")
            if not user_id:
                return None

            user = User.objects.get(id=user_id)
            return user

        except (JWTError, User.DoesNotExist):
            return None


def create_access_token(user, expires_delta: Optional[timedelta] = None):
    """
    Cria um token JWT para o usuário
    """
    to_encode = {
        "user_id": str(user.id),
        "exp": datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    return encoded_jwt


def get_token_for_user(user):
    """
    Gera um token de acesso para o usuário (usado no login)
    """
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        user, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": access_token_expires.total_seconds()
    }