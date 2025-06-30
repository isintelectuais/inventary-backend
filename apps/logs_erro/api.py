from ninja import Router
from django.shortcuts import get_object_or_404
from typing import List, Optional
from django.db import models
from django.core.exceptions import PermissionDenied
from ninja.errors import HttpError
from .models import LogErro
from .schemas import LogErroCreate, LogErroSchema, LogErroFilter
from apps.usuarios.authentication import JWTAuth
from apps.robos.models import Robo

# Sub-routers com autenticação JWT
master_router = Router(auth=JWTAuth())
admin_router = Router(auth=JWTAuth())
robo_router = Router(auth=JWTAuth())

# --- Utils ---
def verificar_admin(user):
    if user.tipo not in ["Master", "Admin"]:
        raise PermissionDenied("Acesso restrito a administradores")

def verificar_master(user):
    if user.tipo != "Master":
        raise PermissionDenied("Apenas usuários Master podem executar esta ação")

# --- MASTER ---
@master_router.delete("/{log_id}")
def deletar_log(request, log_id: int):
    verificar_master(request.auth)
    log = get_object_or_404(LogErro, id=log_id)
    log.delete()
    return {"success": True, "message": "Log removido com sucesso."}

# --- ADMIN ---
@admin_router.post("/", response=LogErroSchema)
def criar_log_admin(request, payload: LogErroCreate):
    verificar_admin(request.auth)

    data = payload.dict()
    if data.get("robo_id"):
        data["robo"] = get_object_or_404(Robo, id=data["robo_id"])
    log = LogErro.objects.create(**data)
    return log

@admin_router.get("/", response=List[LogErroSchema])
def listar_logs(request, filters: LogErroFilter = None, limit: Optional[int] = 100):
    verificar_admin(request.auth)

    queryset = LogErro.objects.all()

    if filters:
        if filters.origem:
            queryset = queryset.filter(origem__icontains=filters.origem)
        if filters.robo_id:
            queryset = queryset.filter(robo_id=filters.robo_id)
        if filters.data_inicio:
            queryset = queryset.filter(data_hora__gte=filters.data_inicio)
        if filters.data_fim:
            queryset = queryset.filter(data_hora__lte=filters.data_fim)

    return queryset.order_by("-data_hora")[:limit]

@admin_router.get("/estatisticas/")
def estatisticas_logs(request):
    verificar_admin(request.auth)

    total = LogErro.objects.count()
    por_origem = (
        LogErro.objects.values("origem")
        .annotate(count=models.Count("id"))
        .order_by("-count")
    )
    por_robo = (
        LogErro.objects.filter(robo__isnull=False)
        .values("robo__identificador")
        .annotate(count=models.Count("id"))
        .order_by("-count")
    )

    return {
        "total_erros": total,
        "erros_por_origem": list(por_origem),
        "erros_por_robo": list(por_robo),
    }

# --- ROBÔ ---
@robo_router.post("/", response={201: dict})
def criar_log_robo(request, payload: LogErroCreate):
    """
    Robôs autenticados (via JWT) reportam erros
    """
    if not hasattr(request.auth, "robo_id"):
        raise PermissionDenied("Este endpoint é exclusivo para robôs")

    robo = get_object_or_404(Robo, id=request.auth.robo_id)

    log = LogErro.objects.create(
        mensagem=payload.mensagem,
        origem=payload.origem,
        robo=robo
    )

    return 201, {"id": log.id, "data_hora": log.data_hora}

# --- Roteador principal ---
log_router = Router()
log_router.add_router("/master", master_router, tags=["Logs Master"])
log_router.add_router("/admin", admin_router, tags=["Logs Admin"])
log_router.add_router("/robo", robo_router, tags=["Logs Robô"])
