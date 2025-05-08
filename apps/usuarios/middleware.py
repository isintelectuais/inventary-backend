import jwt
from django.conf import settings
from django.utils.functional import SimpleLazyObject
from .models import Usuario

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                request.user = SimpleLazyObject(lambda: Usuario.objects.get(id=payload['user_id']))
                print(f"Usuário autenticado: {request.user.email}")  # Debug
            except Exception as e:
                print(f"Falha na autenticação: {e}")  # Debug
        return self.get_response(request)