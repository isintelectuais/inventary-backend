from ninja import Router
from django.shortcuts import get_object_or_404
from typing import List
from django.core.exceptions import PermissionDenied

from . import schemas, models
from ..auth import JWTAuth

router = Router()
auth_router = Router(auth=JWTAuth())

# Sub-roteadores por nível de acesso
master_router = Router(auth=JWTAuth())
admin_router = Router(auth=JWTAuth())
user_router = Router(auth=JWTAuth())


# --- ROTAS MASTER (Exclusivas) ---
@master_router.delete("/imagens/{imagem_id}", response={204: None, 403: dict})
def remover_imagem(request, imagem_id: int):
    """
    Remove uma imagem - EXCLUSIVO para Master
    """
    if request.user.tipo != "Master":
        raise PermissionDenied("Acesso restrito a usuários Master")

    imagem = get_object_or_404(models.ImagemCapturada, id=imagem_id)
    imagem.delete()
    return 204, None


# --- ROTAS ADMIN (Master + Admin) ---
@admin_router.get("/imagens", response=List[schemas.ImagemOut])
def listar_imagens(request, agendamento_id: int = None, robo_id: int = None):
    """
    Lista imagens capturadas - Acessível por Admin e Master
    Filtros opcionais por agendamento ou robô
    """
    queryset = models.ImagemCapturada.objects.all()

    if agendamento_id:
        queryset = queryset.filter(robo__agendamentos__id=agendamento_id)
    if robo_id:
        queryset = queryset.filter(robo_id=robo_id)

    return queryset.order_by('-data_hora')


# --- ROTAS USUÁRIO (Todos autenticados) ---
@user_router.get("/imagens/{imagem_id}", response={200: schemas.ImagemOut, 403: dict})
def visualizar_imagem(request, imagem_id: int):
    """
    Visualiza detalhes de uma imagem específica
    - Master e Admin podem ver qualquer imagem
    - Usuários comuns só veem imagens de seus armazéns
    """
    imagem = get_object_or_404(models.ImagemCapturada, id=imagem_id)

    if request.user.tipo not in ["Master", "Admin"]:
        if not models.Agendamento.objects.filter(
                robo=imagem.robo,
                armazem_id__in=request.user.armazens_permitidos.values_list('id')
        ).exists():
            raise PermissionDenied("Acesso não autorizado a esta imagem")

    return imagem


@user_router.get("/imagens/por-endereco/{codigo_endereco}", response=List[schemas.ImagemOut])
def listar_imagens_por_endereco(request, codigo_endereco: str):
    """
    Lista imagens por código de endereço (formato: cidade:bairro:rua:predio:nivel:apto)
    """
    queryset = models.ImagemCapturada.objects.filter(
        codigo_lido__contains=codigo_endereco
    ).order_by('-data_hora')

    if request.user.tipo not in ["Master", "Admin"]:
        queryset = queryset.filter(
            robo__armazem_id__in=request.user.armazens_permitidos.values_list('id')
        )

    return queryset


# Montagem da hierarquia de roteadores
auth_router.add_router("/master", master_router, tags=["Imagens-Master"])
auth_router.add_router("/admin", admin_router, tags=["Imagens-Admin"])
auth_router.add_router("/user", user_router, tags=["Imagens-Usuario"])
router.add_router("", auth_router)