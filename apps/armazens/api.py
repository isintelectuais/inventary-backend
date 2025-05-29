from ninja import Router
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from typing import List
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from . import schemas, models, exceptions
from apps.usuarios.authentication import JWTAuth

# Criação dos roteadores principais
router = Router()  # Rotas públicas
auth_router = Router(auth=JWTAuth())

# Sub-roteadores por nível de acesso
master_router = Router(auth=JWTAuth())
admin_router = Router(auth=JWTAuth())
user_router = Router(auth=JWTAuth())


# --- ROTAS MASTER (Exclusivas) ---
@master_router.post("/armazens", response={201: schemas.ArmazemOut, 400: dict})
def criar_armazem(request, payload: schemas.ArmazemIn):
    """
    Cria um novo armazém - EXCLUSIVO para usuários Master
    """
    if request.user.tipo != "Master":
        raise PermissionDenied("Acesso restrito a usuários Master")

    try:
        # Validação de campos obrigatórios
        campos_obrigatorios = {
            'codigo_armazem': payload.codigo_armazem,
            'nome': payload.nome,
            'qtd_niveis': payload.qtd_niveis,
            'qtd_cidades': payload.qtd_cidades,
            'qtd_bairros_por_cidade': payload.qtd_bairros_por_cidade,
            'qtd_ruas_por_bairro': payload.qtd_ruas_por_bairro,
            'qtd_predios_por_rua': payload.qtd_predios_por_rua
        }

        for campo, valor in campos_obrigatorios.items():
            if valor is None or (isinstance(valor, str) and not valor.strip()):
                return JsonResponse({"error": f"O campo {campo} não pode estar vazio"}, status=400)

        armazem = models.Armazem.objects.create(**payload.dict())
        return 201, armazem

    except IntegrityError as e:
        if 'codigo_armazem' in str(e):
            raise exceptions.DuplicateArmazemCode()
        raise exceptions.InvalidArmazemData("Erro de integridade no banco de dados")
    except ValidationError as e:
        raise exceptions.InvalidArmazemData(str(e))


@master_router.delete("/armazens/{armazem_id}", response={204: None, 403: dict})
def remover_armazem(request, armazem_id: int):
    """
    Remove (desativa) um armazém - EXCLUSIVO para Master
    """
    if request.user.tipo != "Master":
        raise PermissionDenied("Acesso restrito a usuários Master")

    armazem = get_object_or_404(models.Armazem, id=armazem_id)
    armazem.ativo = False
    armazem.save()
    return 204, None


# --- ROTAS ADMIN (Master + Admin) ---
@master_router.post("/armazens", response={201: schemas.ArmazemOut, 400: dict})
@admin_router.get("/armazens", response=List[schemas.ArmazemOut])
def listar_armazens(request):
    """
    Lista todos os armazéns ativos - Acessível por Admin e Master
    """
    if request.user.tipo not in ["Admin", "Master"]:
        raise PermissionDenied("Acesso restrito a administradores")

    return models.Armazem.objects.filter(ativo=True)

@master_router.post("/armazens/{armazem_id}", response={201: schemas.ArmazemOut, 400: dict})
@admin_router.put("/armazens/{armazem_id}", response={200: schemas.ArmazemOut, 400: dict})
def atualizar_armazem(request, armazem_id: int, payload: schemas.ArmazemUpdate):
    """
    Atualiza informações de um armazém - Acessível por Admin e Master
    """
    if request.user.tipo not in ["Admin", "Master"]:
        raise PermissionDenied("Acesso restrito a administradores")

    armazem = get_object_or_404(models.Armazem, id=armazem_id)

    # Validação de campos vazios
    update_data = payload.dict(exclude_unset=True)
    for campo, valor in update_data.items():
        if isinstance(valor, str) and not valor.strip():
            return JsonResponse({"error": f"O campo {campo} não pode estar vazio"}, status=400)

    # Aplica atualizações
    for attr, value in update_data.items():
        setattr(armazem, attr, value)

    try:
        armazem.save()
        return armazem
    except IntegrityError as e:
        if 'codigo_armazem' in str(e):
            raise exceptions.DuplicateArmazemCode()
        raise exceptions.InvalidArmazemData("Erro de integridade no banco de dados")
    except ValidationError as e:
        raise exceptions.InvalidArmazemData(str(e))


# --- ROTAS USUÁRIO (Todos autenticados com permissão) ---
@user_router.get("/armazens/{armazem_id}", response={200: schemas.ArmazemOut, 403: dict})
def visualizar_armazem(request, armazem_id: int):
    """
    Visualiza detalhes de um armazém específico
    - Master e Admin podem ver qualquer armazém
    - Usuários comuns só veem armazéns permitidos
    """
    # Master e Admin têm acesso livre
    if request.user.tipo not in ["Master", "Admin"]:
        # Verifica permissão para usuários comuns
        if not models.Armazem.objects.filter(
                id=armazem_id,
                ativo=True,
                id__in=request.user.armazens_permitidos.values_list('id')
        ).exists():
            raise PermissionDenied("Acesso não autorizado a este armazém")

    armazem = get_object_or_404(models.Armazem, id=armazem_id, ativo=True)
    return armazem


@user_router.get("/armazens/meus", response=List[schemas.ArmazemOut])
def listar_meus_armazens(request):
    """
    Lista armazéns acessíveis pelo usuário
    - Master e Admin veem todos
    - Usuários comuns veem apenas os permitidos
    """
    if request.user.tipo in ["Master", "Admin"]:
        return models.Armazem.objects.filter(ativo=True)

    return models.Armazem.objects.filter(
        ativo=True,
        id__in=request.user.armazens_permitidos.values_list('id')
    )


# --- Montagem da hierarquia de roteadores ---
auth_router.add_router("/master", master_router, tags=["Master"])
auth_router.add_router("/admin", admin_router, tags=["Admin"])
auth_router.add_router("/user", user_router, tags=["Usuario"])
router.add_router("", auth_router)