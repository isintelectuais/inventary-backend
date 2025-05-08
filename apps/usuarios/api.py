from ninja import Router
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
import jwt
import uuid
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from datetime import datetime, timedelta
from django.conf import settings
from .models import Usuario
from .authentication import JWTAuth
from ninja_jwt.tokens import RefreshToken
from .schemas import UsuarioOut, AlterarSenha, LoginSchema, UsuarioCreate, AdminCriaUsuarioSchema

# Cria roteadores separados para cada tipo de usuário
router = Router()  # Router principal
master_router = Router()
admin_router = Router()
usuarios_router = Router()


# --- ROTA PÚBLICA (ACESSÍVEL A TODOS) ---
@router.post("/login", response={200: dict, 401: dict})
def login(request, dados: LoginSchema):
    try:
        # Busca usuário por email ou matrícula
        if dados.email:
            usuario = Usuario.objects.get(email=dados.email)
        elif dados.matricula:
            usuario = Usuario.objects.get(matricula=dados.matricula)
        else:
            return JsonResponse({"error": "Email ou matrícula é obrigatório"}, status=400)

        # Verifica a senha
        if not check_password(dados.senha, usuario.password):
            return JsonResponse({"error": "Credenciais inválidas"}, status=401)

        # Cria payload do token
        payload = {
            "token_type": "access",
            "exp": datetime.utcnow() + timedelta(hours=2),
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4()),
            "user_id": usuario.id,
            "tipo": usuario.tipo
        }

        # Gera token JWT
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm="HS256"
        )

        return JsonResponse({
            "access": token,
            "tipo": usuario.tipo,
            "nome": usuario.nome
        })

    except Usuario.DoesNotExist:
        return JsonResponse({"error": "Usuário não encontrado"}, status=401)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



# --- ROTAS PROTEGIDAS ---

# Rotas para Master
@master_router.post("/criar-usuario", response={201: UsuarioOut, 400: dict, 403: dict}, auth=JWTAuth())
def criar_usuario_master(request, usuario_data: UsuarioCreate):
    # Verificação de permissão
    if not hasattr(request, 'user') or request.user.tipo != "Master":
        return JsonResponse({"error": "Permissão negada. Apenas Master pode criar usuários."}, status=403)

    # Lista de campos obrigatórios para validação
    campos_obrigatorios = {
        'nome': usuario_data.nome,
        'email': usuario_data.email,
        'matricula': usuario_data.matricula,
        'departamento': usuario_data.departamento,
        'cargo': usuario_data.cargo,
        'tipo': usuario_data.tipo,
        'senha': usuario_data.senha,
        'confirmar_senha': usuario_data.confirmar_senha
    }

    # Validação de campos vazios ou com apenas espaços em branco
    for campo, valor in campos_obrigatorios.items():
        if not valor or (isinstance(valor, str) and valor.strip() == ""):
            return JsonResponse({"error": f"O campo {campo} não pode estar vazio"}, status=400)

    # Validação adicional de tipo de usuário
    if usuario_data.tipo not in ["Master", "Admin", "Usuario"]:
        return JsonResponse({"error": "Tipo de usuário inválido"}, status=400)

    # Validação de confirmação de senha
    if usuario_data.senha != usuario_data.confirmar_senha:
        return JsonResponse({"error": "As senhas não coincidem"}, status=400)

    try:
        # Criação do usuário com tratamento de strings
        usuario_db = Usuario.objects.create(
            nome=usuario_data.nome.strip(),
            email=usuario_data.email.strip().lower(),
            matricula=usuario_data.matricula.strip(),
            departamento=usuario_data.departamento.strip(),
            cargo=usuario_data.cargo.strip(),
            tipo=usuario_data.tipo,
            password=make_password(usuario_data.senha)
        )

        # Resposta formatada manualmente
        return 201, {
            "id": usuario_db.id,
            "nome": usuario_db.nome,
            "email": usuario_db.email,
            "matricula": usuario_db.matricula,
            "departamento": usuario_db.departamento,
            "cargo": usuario_db.cargo,
            "tipo": usuario_db.tipo
        }

    except IntegrityError as e:
        # Tratamento específico para erros de integridade
        if 'email' in str(e):
            return JsonResponse({"error": "Este email já está cadastrado"}, status=400)
        elif 'matricula' in str(e):
            return JsonResponse({"error": "Esta matrícula já está cadastrada"}, status=400)
        return JsonResponse({"error": "Erro ao criar usuário"}, status=400)

# Rotas para listar usuários
@admin_router.get("/listar-usuarios", response={200: list[UsuarioOut]}, auth=JWTAuth())
@master_router.get("/listar-usuarios", response={200: list[UsuarioOut]}, auth=JWTAuth())
def listar_usuarios(request):
    if not hasattr(request, 'user') or request.user.tipo not in ["Admin", "Master"]:
        return JsonResponse({"error": "Permissão negada"}, status=403)

    usuarios = Usuario.objects.all()
    return [usuario.to_dict() for usuario in usuarios]

# Rotas Admin
@admin_router.post("/criar-usuario-comum", response={201: UsuarioOut, 400: dict, 403: dict}, auth=JWTAuth())
def criar_usuario_comum(request, usuario_data: UsuarioCreate):
    # Verificação de permissão
    if not hasattr(request, 'user') or request.user.tipo not in ["Admin", "Master"]:
        return JsonResponse({"error": "Permissão negada"}, status=403)

    # Validação de campos obrigatórios
    campos_obrigatorios = {
        'nome': usuario_data.nome,
        'email': usuario_data.email,
        'matricula': usuario_data.matricula,
        'departamento': usuario_data.departamento,
        'cargo': usuario_data.cargo,
        'senha': usuario_data.senha,
        'confirmar_senha': usuario_data.confirmar_senha
    }

    for campo, valor in campos_obrigatorios.items():
        if not valor or (isinstance(valor, str) and valor.strip() == ""):
            return JsonResponse({"error": f"O campo {campo} é obrigatório"}, status=400)

    # Validação de confirmação de senha (redundante com schema, mas importante)
    if usuario_data.senha != usuario_data.confirmar_senha:
        return JsonResponse({"error": "As senhas não coincidem"}, status=400)

    # SEMPRE cria como "Usuario", mesmo se chamado por Master
    try:
        usuario_db = Usuario.objects.create(
            nome=usuario_data.nome.strip(),
            email=usuario_data.email.strip(),
            matricula=usuario_data.matricula.strip(),
            departamento=usuario_data.departamento.strip(),
            cargo=usuario_data.cargo.strip(),
            tipo="Usuario",  # Forçado independente do input
            password=make_password(usuario_data.senha)
        )
        return 201, usuario_db.to_dict()

    except IntegrityError as e:
        error_msg = "Email já existe" if 'email' in str(e) else "Matrícula já existe"
        return JsonResponse({"error": error_msg}, status=400)

@router.post("/refresh-token", response={200: dict, 401: dict})
def refresh_token(request, dados: dict):  # Aceita um dicionário simples
    try:
        refresh_token = dados.get("refresh")
        if not refresh_token:
            return JsonResponse({"error": "Refresh token é obrigatório"}, status=400)

        refresh = RefreshToken(refresh_token)
        new_access_token = str(refresh.access_token)

        return JsonResponse({
            "access": new_access_token,
        })
    except Exception as e:
        return JsonResponse({"error": "Token inválido ou expirado"}, status=401)


# Rotas para Admin e Master (Deletar usuário)
@admin_router.delete("/deletar-usuario/{usuario_id}", response={200: dict, 404: dict, 403: dict}, auth=JWTAuth())
@master_router.delete("/deletar-usuario/{usuario_id}", response={200: dict, 404: dict, 403: dict}, auth=JWTAuth())
def deletar_usuario(request, usuario_id: int):
    """
    Endpoint para deletar um usuário - apenas Admin ou Master podem acessar
    """
    if request.user.tipo not in ["Admin", "Master"]:
        return JsonResponse({"error": "Permissão negada. Apenas Admin ou Master podem deletar usuários."}, status=403)

    try:
        usuario = Usuario.objects.get(id=usuario_id)
        usuario.delete()
        return JsonResponse({"message": "Usuário deletado com sucesso."})
    except Usuario.DoesNotExist:
        return JsonResponse({"error": "Usuário não encontrado."}, status=404)


# Rota para alterar senha
@master_router.post("/alterar-senha", response={200: dict, 400: dict, 403: dict, 404: dict}, auth=JWTAuth())
@admin_router.post("/alterar-senha", response={200: dict, 400: dict, 403: dict, 404: dict}, auth=JWTAuth())
def alterar_senha(request, dados: AlterarSenha):
    # Verificação de permissão
    if request.user.tipo not in ["Admin", "Master"]:
        return JsonResponse({"error": "Permissão negada"}, status=403)

    try:
        # Verifica campos vazios
        if not all([dados.usuario_id, dados.senha_atual, dados.nova_senha, dados.confirmar_senha]):
            return JsonResponse({"error": "Todos os campos são obrigatórios"}, status=400)

        # Verifica se as novas senhas coincidem
        if dados.nova_senha != dados.confirmar_senha:
            return JsonResponse({"error": "A nova senha e a confirmação não coincidem"}, status=400)

        # Verifica se a nova senha é diferente da atual
        if dados.nova_senha == dados.senha_atual:
            return JsonResponse({"error": "A nova senha deve ser diferente da atual"}, status=400)

        # Verifica tamanho mínimo da senha
        if len(dados.nova_senha) < 6:
            return JsonResponse({"error": "A senha deve ter no mínimo 8 caracteres"}, status=400)

        usuario = Usuario.objects.get(id=dados.usuario_id)

        # Verifica senha atual
        if not check_password(dados.senha_atual, usuario.password):
            return JsonResponse({"error": "Senha atual incorreta"}, status=400)

        # Atualiza a senha
        usuario.password = make_password(dados.nova_senha)
        usuario.save()

        return JsonResponse({"message": "Senha alterada com sucesso"})

    except Usuario.DoesNotExist:
        return JsonResponse({"error": "Usuário não encontrado"}, status=404)

# Combina todos os roteadores
router.add_router("/master", master_router, tags=["Master"])
router.add_router("/admin", admin_router, tags=["Admin"])
router.add_router("/usuarios", usuarios_router, tags=["Usuario"])
