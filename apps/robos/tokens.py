import jwt
from django.conf import settings
from .models import Robo


def gerar_token_robo(robo: Robo) -> str:
    """
    Gera um token JWT para autenticação do robô

    Args:
        robo: Instância do modelo Robo

    Returns:
        str: Token JWT assinado
    """
    payload = {
        'robo_id': robo.id,
        'identificador': robo.identificador,
        'tipo': 'robo'
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')