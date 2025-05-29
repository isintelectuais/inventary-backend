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
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
                options={"verify_exp": True}
            )

            # Se for um robô
            if 'robo_id' in payload:
                logger.debug(f"Autenticando robô ID: {payload['robo_id']}")
                robo = Robo.objects.get(id=payload['robo_id'])
                # Adiciona o robo_id ao objeto de autenticação
                robo.auth_data = {'robo_id': robo.id}
                return robo

            # Autenticação normal de usuário
            user = Usuario.objects.get(id=payload['user_id'])
            return user

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expirado")
        except (jwt.InvalidTokenError, Usuario.DoesNotExist, Robo.DoesNotExist) as e:
            raise AuthenticationFailed("Credenciais inválidas")