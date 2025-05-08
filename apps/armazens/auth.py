from ninja.security import APIKeyHeader
from django.contrib.auth import get_user_model
from jose import jwt
from django.conf import settings

User = get_user_model()


class JWTAuth(APIKeyHeader):
    param_name = "Authorization"

    def authenticate(self, request, key):
        try:
            token = key.split(" ")[1]  # Remove "Bearer "
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload['user_id'])
            return user
        except (IndexError, jwt.JWTError, User.DoesNotExist):
            return None


def master_required(request):
    if not request.auth or request.auth.tipo != 'master':
        raise PermissionDenied("Acesso restrito a usuários Master")


def admin_required(request):
    if not request.auth or request.auth.tipo not in ['master', 'admin']:
        raise PermissionDenied("Acesso restrito a administradores")


def user_has_armazem_access(armazem_id):
    def decorator(request):
        user = request.auth
        if not user:
            raise PermissionDenied("Usuário não autenticado")

        if user.tipo in ['master', 'admin']:
            return True

        # Verifica se usuário comum tem acesso ao armazém
        if not user.armazens_permitidos.filter(id=armazem_id).exists():
            raise PermissionDenied("Acesso não autorizado a este armazém")

    return decorator