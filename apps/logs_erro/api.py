from datetime import datetime
from typing import List, Optional
from ninja import NinjaAPI, Query
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from .models import LogErro
from .schemas import LogErroCreate, LogErroSchema, LogErroFilter
from robos.models import Robo
from apps.usuarios.authenticate import JWTAuth

# Única API com autenticação JWT
api = NinjaAPI(urls_namespace='logs_erro', auth=JWTAuth())


def verificar_admin(user):
    """Verifica se o usuário é Admin ou Master"""
    if user.tipo not in ["Master", "Admin"]:
        raise PermissionDenied("Acesso restrito a administradores")


def verificar_master(user):
    """Verifica se o usuário é Master"""
    if user.tipo != "Master":
        raise PermissionDenied("Apenas usuários Master podem executar esta ação")


@api.post("/criar-log-erro-admin", response=LogErroSchema)
def criar_log_erro_admin(request, payload: LogErroCreate):
    """
    Cria um novo log de erro no sistema.
    Apenas Admin e Master podem criar logs manualmente.
    """
    verificar_admin(request.auth)

    log_data = payload.dict()

    if log_data.get('robo_id'):
        robo = get_object_or_404(Robo, id=log_data['robo_id'])
        log_data['robo'] = robo

    log = LogErro.objects.create(**log_data)
    return log


@api.post("/criar-log-erro-robo")
def criar_log_erro_robo(request, payload: LogErroCreate):
    """
    Endpoint para robôs reportarem erros.
    O token JWT deve conter 'robo_id' no payload.
    """
    if not hasattr(request.auth, 'robo_id'):
        raise PermissionDenied("Este endpoint é exclusivo para robôs")

    # Obtém o robô associado ao token
    robo = get_object_or_404(Robo, id=request.auth.robo_id)

    log = LogErro.objects.create(
        mensagem=payload.mensagem,
        origem=payload.origem,
        robo=robo
    )
    return {"id": log.id, "data_hora": log.data_hora}


@api.get("/listar-logs-erro", response=List[LogErroSchema])
def listar_logs_erro(
        request,
        filters: LogErroFilter = Query(...),
        limit: Optional[int] = 100
):
    """
    Lista os logs de erro com possibilidade de filtro.
    Apenas Admin e Master podem visualizar.
    """
    verificar_admin(request.auth)

    queryset = LogErro.objects.all()

    if filters.origem:
        queryset = queryset.filter(origem__icontains=filters.origem)

    if filters.robo_id:
        queryset = queryset.filter(robo_id=filters.robo_id)

    if filters.data_inicio:
        queryset = queryset.filter(data_hora__gte=filters.data_inicio)

    if filters.data_fim:
        queryset = queryset.filter(data_hora__lte=filters.data_fim)

    return queryset.order_by('-data_hora')[:limit]


@api.delete("/deletar-log-erro/{log_id}")
def deletar_log_erro(request, log_id: int):
    """
    Remove um log de erro do sistema.
    Apenas Master pode deletar logs permanentemente.
    """
    verificar_master(request.auth)

    log = get_object_or_404(LogErro, id=log_id)
    log.delete()
    return {"success": True, "message": "Log de erro removido com sucesso."}


@api.get("/estatisticas/")
def estatisticas_erros(request):
    """
    Retorna estatísticas sobre os logs de erro.
    """
    total_erros = LogErro.objects.count()
    erros_por_origem = (
        LogErro.objects.values('origem')
        .annotate(count=models.Count('id'))
        .order_by('-count')
    )
    erros_por_robo = (
        LogErro.objects.filter(robo__isnull=False)
        .values('robo__identificador')
        .annotate(count=models.Count('id'))
        .order_by('-count')
    )

    return {
        "total_erros": total_erros,
        "erros_por_origem": list(erros_por_origem),
        "erros_por_robo": list(erros_por_robo),
    }