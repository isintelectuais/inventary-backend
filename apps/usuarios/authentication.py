from ninja.security import HttpBearer
from django.conf import settings
import jwt
from ninja_extra.exceptions import AuthenticationFailed
from .models import Usuario
import logging

logger = logging.getLogger(__name__)


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            # DEBUG: Mostra o token recebido
            logger.debug(f"Token recebido: {token}")

            payload = jwt.decode(
                token,
                settings.SECRET_KEY,  # Deve ser igual ao usado na criação
                algorithms=["HS256"],
                options={"verify_exp": True}
            )

            # DEBUG: Mostra o payload decodificado
            logger.debug(f"Payload decodificado: {payload}")

            user = Usuario.objects.get(id=payload['user_id'])
            return user

        except jwt.ExpiredSignatureError:
            logger.warning("Token expirado")
            raise AuthenticationFailed("Token expirado")
        except jwt.InvalidTokenError as e:
            logger.error(f"Token inválido: {str(e)}")
            raise AuthenticationFailed("Token inválido")
        except Usuario.DoesNotExist:
            logger.error("Usuário não encontrado no banco")
            raise AuthenticationFailed("Usuário não encontrado")