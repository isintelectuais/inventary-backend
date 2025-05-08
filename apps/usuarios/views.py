from ninja import Router
from ninja.security import HttpBearer
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from datetime import datetime, timedelta
from django.conf import settings
from .models import Usuario
from .authentication import JWTAuth
from .schemas import UsuarioOut, AlterarSenha, LoginSchema, UsuarioCreate

router = Router()

# Criar novo usuário
@router.post("/usuarios/criar-usuario", response=UsuarioOut, auth=JWTAuth())
def criar_usuario(request, usuario_data: UsuarioCreate):
    # Verificar se o usuário está autenticado corretamente
    usuario_logado = request.user
    if not usuario_logado:
        return JsonResponse({"error": "Usuário não autenticado."}, status=401)

    # Verificar se o usuário logado tem permissão para criar um novo usuário
    if usuario_logado.tipo not in ["Master", "Admin"]:
        return JsonResponse({"error": "Permissão negada. Apenas usuários Master ou Admin podem criar usuários."}, status=403)

    # Verificar se todos os campos obrigatórios foram fornecidos
    if not all([usuario_data.email, usuario_data.matricula, usuario_data.senha, usuario_data.tipo]):
        return JsonResponse({"error": "Todos os campos obrigatórios devem ser preenchidos."}, status=400)

    # Verificar se o email ou matrícula já existem
    if Usuario.objects.filter(email=usuario_data.email).exists() or Usuario.objects.filter(matricula=usuario_data.matricula).exists():
        return JsonResponse({"error": "Email ou matrícula já existe."}, status=400)

    # Verificar se a senha tem pelo menos 6 caracteres
    if len(usuario_data.senha) < 6:
        return JsonResponse({"error": "A senha deve ter pelo menos 6 caracteres."}, status=400)

    try:
        # Criar o novo usuário no banco de dados
        usuario_db = Usuario.objects.create(
            email=usuario_data.email,
            nome=usuario_data.nome,
            matricula=usuario_data.matricula,
            departamento=usuario_data.departamento,
            cargo=usuario_data.cargo,
            tipo=usuario_data.tipo,
            password=make_password(usuario_data.senha)  # Sempre usar make_password para segurança da senha
        )
    except IntegrityError:
        return JsonResponse({"error": "Erro ao criar usuário. Verifique se os dados estão corretos."}, status=400)

    return JsonResponse({"success": "Usuário criado com sucesso.", "usuario": usuario_db.to_dict()})

# Exemplo de Login para gerar o token
@router.post("/usuarios/login")
def login(request, usuario_data: LoginSchema):
    try:
        # Verifique se o usuário existe
        usuario = Usuario.objects.get(email=usuario_data.email)

        # Verifique a senha
        if not usuario.check_password(usuario_data.senha):
            return JsonResponse({"error": "Credenciais inválidas."}, status=401)

        # Crie o token de acesso
        token = JWTAuth.create_access_token(usuario)

        return JsonResponse({"token": token, "tipo": usuario.tipo, "nome": usuario.nome})

    except Usuario.DoesNotExist:
        return JsonResponse({"error": "Usuário não encontrado."}, status=404)

# Alterar senha
@router.put("/usuarios/alterar-senha", response=UsuarioOut, auth=JWTAuth())
def alterar_senha(request, dados: AlterarSenha):
    usuario = request.user

    if not check_password(dados.senha_atual, usuario.password):
        raise PermissionDenied("Senha atual incorreta")

    if dados.nova_senha != dados.confirmar_senha:
        raise PermissionDenied("As novas senhas não coincidem")

    if len(dados.nova_senha) < 6:
        raise PermissionDenied("A nova senha deve ter pelo menos 6 caracteres")

    usuario.password = make_password(dados.nova_senha)
    usuario.save()

    return usuario

# Listar usuários (permite Admin ou Master)
@router.get("/usuarios/", response=list[UsuarioOut], auth=JWTAuth())
def listar_usuarios(request):
    usuario_atual = request.user

    if usuario_atual.tipo == "Master":
        return Usuario.objects.all()

    if usuario_atual.tipo == "Admin":
        return Usuario.objects.filter(tipo="Usuario")

    raise PermissionDenied("Você não tem permissão para ver essa lista")

# Excluir usuário
@router.delete("/usuarios/{usuario_id}", auth=JWTAuth())
def excluir_usuario(request, usuario_id: int):
    usuario_logado = request.user

    # Apenas Master pode excluir usuários
    if usuario_logado.tipo != "Master":
        return JsonResponse({"error": "Somente o Master pode excluir usuários."}, status=403)

    try:
        usuario = Usuario.objects.get(id=usuario_id)
        usuario.delete()
        return JsonResponse({"success": "Usuário excluído com sucesso."})
    except Usuario.DoesNotExist:
        return JsonResponse({"error": "Usuário não encontrado."}, status=404)

# Função para login como admin
@router.post("/usuarios/login-admin", response=UsuarioOut)
def login_admin(request, dados: LoginSchema):
    # Utiliza a autenticação do JWT
    usuario_logado = JWTAuth().authenticate(request, dados.token)

    if not usuario_logado:
        return JsonResponse({"error": "Credenciais inválidas."}, status=401)

    if usuario_logado.tipo not in ["Admin", "Master"]:
        return JsonResponse({"error": "Permissão negada. Somente Admin ou Master podem acessar."}, status=403)

    payload = {
        "user_id": usuario_logado.id,
        "exp": datetime.utcnow() + timedelta(hours=2),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    return JsonResponse({"token": token, "tipo": usuario_logado.tipo})
