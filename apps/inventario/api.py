from ninja import Router
from django.shortcuts import get_object_or_404
from typing import List
from django.core.exceptions import PermissionDenied

from . import schemas, models
from apps.usuarios.authentication import JWTAuth

router = Router()
auth_router = Router(auth=JWTAuth())

# Sub-roteadores por nível de acesso
master_router = Router(auth=JWTAuth())
admin_router = Router(auth=JWTAuth())
user_router = Router(auth=JWTAuth())


# --- ROTAS MASTER (Exclusivas) ---
@master_router.get("/inventario/estatisticas", response=schemas.EstatisticasInventario)
def estatisticas_inventario(request):
    """
    Estatísticas completas do inventário - EXCLUSIVO para Master
    """
    if request.user.tipo != "Master":
        raise PermissionDenied("Acesso restrito a usuários Master")

    total_armazens = models.Armazem.objects.count()
    total_registros = models.Inventario.objects.count()
    ultimo_inventario = models.Inventario.objects.order_by('-data_hora').first()

    return {
        "total_armazens": total_armazens,
        "total_registros": total_registros,
        "ultimo_inventario": ultimo_inventario.data_hora if ultimo_inventario else None
    }


# --- ROTAS ADMIN (Master + Admin) ---
@admin_router.post("/inventario/registrar", response={201: schemas.InventarioOut})
def registrar_inventario(request, payload: schemas.InventarioIn):
    """
    Registrar novo item no inventário - Acessível por Admin e Master
    """
    # Verifica se o robô pertence a um armazém que o usuário tem acesso
    if request.user.tipo not in ["Master", "Admin"]:
        raise PermissionDenied("Acesso restrito a administradores")

    agendamento = get_object_or_404(models.Agendamento, id=payload.agendamento_id)

    # Para Admin, verifica se o armazém está nos permitidos
    if request.user.tipo == "Admin":
        if agendamento.armazem_id not in request.user.armazens_permitidos.values_list('id'):
            raise PermissionDenied("Acesso não autorizado a este armazém")

    inventario = models.Inventario.objects.create(
        agendamento=agendamento,
        codigo_palete=payload.codigo_palete,
        codigo_endereco=payload.codigo_endereco
    )

    return 201, inventario


@admin_router.get("/inventario/por-armazem/{armazem_id}", response=List[schemas.InventarioOut])
def listar_inventario_armazem(request, armazem_id: int):
    """
    Lista itens do inventário por armazém - Acessível por Admin e Master
    """
    if request.user.tipo == "Admin":
        if armazem_id not in request.user.armazens_permitidos.values_list('id'):
            raise PermissionDenied("Acesso não autorizado a este armazém")

    return models.Inventario.objects.filter(
        agendamento__armazem_id=armazem_id
    ).order_by('-data_hora')


# --- ROTAS USUÁRIO (Todos autenticados) ---
@user_router.get("/inventario/meus", response=List[schemas.InventarioOut])
def listar_meu_inventario(request):
    """
    Lista itens do inventário nos armazéns permitidos ao usuário
    """
    if request.user.tipo in ["Master", "Admin"]:
        return models.Inventario.objects.all().order_by('-data_hora')

    return models.Inventario.objects.filter(
        agendamento__armazem_id__in=request.user.armazens_permitidos.values_list('id')
    ).order_by('-data_hora')


@user_router.get("/inventario/por-agendamento/{agendamento_id}", response=List[schemas.InventarioOut])
def listar_inventario_agendamento(request, agendamento_id: int):
    """
    Lista itens do inventário por agendamento
    """
    agendamento = get_object_or_404(models.Agendamento, id=agendamento_id)

    if request.user.tipo not in ["Master", "Admin"]:
        if agendamento.armazem_id not in request.user.armazens_permitidos.values_list('id'):
            raise PermissionDenied("Acesso não autorizado a este agendamento")

    return models.Inventario.objects.filter(
        agendamento_id=agendamento_id
    ).order_by('-data_hora')


@user_router.get("/inventario/dashboard", response=schemas.DashboardInventario)
def dashboard_inventario(request):
    """
    Dashboard com estatísticas do inventário
    """
    if request.user.tipo in ["Master", "Admin"]:
        armazens = models.Armazem.objects.all()
    else:
        armazens = request.user.armazens_permitidos.all()

    resultados = []
    for armazem in armazens:
        count = models.Inventario.objects.filter(
            agendamento__armazem=armazem
        ).count()

        resultados.append({
            "armazem": armazem.nome,
            "total_itens": count,
            "ultimo_registro": models.Inventario.objects.filter(
                agendamento__armazem=armazem
            ).order_by('-data_hora').first().data_hora if count > 0 else None
        })

    return {"armazens": resultados}


# Montagem da hierarquia de roteadores
auth_router.add_router("/master", master_router, tags=["Inventario-Master"])
auth_router.add_router("/admin", admin_router, tags=["Inventario-Admin"])
auth_router.add_router("/user", user_router, tags=["Inventario-Usuario"])
router.add_router("", auth_router)