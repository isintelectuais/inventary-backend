from ninja import Router
from django.shortcuts import get_object_or_404
from django.db.models import Count
from typing import List
from datetime import datetime, timedelta
from ninja.errors import HttpError
from django.core.exceptions import PermissionDenied, ValidationError

from . import schemas, models
from usuarios.authentication import JWTAuth
from .utils import calcular_percentuais

router = Router()
auth_router = Router(auth=JWTAuth())

# Sub-roteadores por nível de acesso
master_router = Router(auth=JWTAuth())
admin_router = Router(auth=JWTAuth())
user_router = Router(auth=JWTAuth())


# --- ROTAS MASTER (Exclusivas) ---
@master_router.get("/agendamentos/estatisticas", response=schemas.EstatisticasAgendamento)
def estatisticas_agendamentos(request):
    """
    Estatísticas completas de agendamentos - EXCLUSIVO para Master
    """
    if request.user.tipo != "Master":
        raise PermissionDenied("Acesso restrito a usuários Master")

    total = models.Agendamento.objects.count()

    # Agendamentos por status
    por_status = models.Agendamento.objects.values('status').annotate(
        quantidade=Count('id')
    ).order_by('-quantidade')

    # Calcula percentuais
    por_status_com_percentual = calcular_percentuais(por_status, total)

    # Próximos agendamentos (7 dias)
    data_inicio = datetime.now()
    data_fim = data_inicio + timedelta(days=7)
    proximos = models.Agendamento.objects.filter(
        data_inicio__range=[data_inicio, data_fim]
    ).order_by('data_inicio')[:5]

    return {
        "total": total,
        "por_status": por_status_com_percentual,
        "proximos": proximos
    }


# --- ROTAS ADMIN (Master + Admin) ---
@admin_router.post("/agendamentos", response={201: schemas.AgendamentoOut, 400: dict})
def criar_agendamento(request, payload: schemas.AgendamentoIn):
    """
    Cria um novo agendamento - Acessível por Admin e Master
    """
    try:
        # Verifica se o usuário tem permissão para o armazém
        if request.user.tipo == "Admin":
            if payload.armazem_id not in request.user.armazens_permitidos.values_list('id'):
                raise PermissionDenied("Acesso não autorizado a este armazém")

        agendamento = models.Agendamento.objects.create(
            **payload.dict(),
            usuario=request.user
        )
        return 201, agendamento
    except ValidationError as e:
        raise HttpError(400, str(e))
    except IntegrityError as e:
        raise HttpError(400, "Erro ao criar agendamento")


@admin_router.put("/agendamentos/{agendamento_id}", response={200: schemas.AgendamentoOut, 400: dict})
def atualizar_agendamento(request, agendamento_id: int, payload: schemas.AgendamentoUpdate):
    """
    Atualiza um agendamento existente - Acessível por Admin e Master
    """
    agendamento = get_object_or_404(models.Agendamento, id=agendamento_id)

    # Verifica permissão
    if request.user.tipo == "Admin":
        if agendamento.armazem_id not in request.user.armazens_permitidos.values_list('id'):
            raise PermissionDenied("Acesso não autorizado a este agendamento")

    try:
        for attr, value in payload.dict(exclude_unset=True).items():
            setattr(agendamento, attr, value)

        agendamento.save()
        return agendamento
    except ValidationError as e:
        raise HttpError(400, str(e))


@admin_router.delete("/agendamentos/{agendamento_id}", response={204: None, 403: dict})
def cancelar_agendamento(request, agendamento_id: int):
    """
    Cancela um agendamento - Acessível por Admin e Master
    """
    agendamento = get_object_or_404(models.Agendamento, id=agendamento_id)

    # Verifica permissão
    if request.user.tipo == "Admin":
        if agendamento.armazem_id not in request.user.armazens_permitidos.values_list('id'):
            raise PermissionDenied("Acesso não autorizado a este agendamento")

    # Só pode cancelar se não estiver em andamento ou concluído
    if agendamento.status in ['em_andamento', 'concluido']:
        raise HttpError(400, "Agendamento já em andamento ou concluído não pode ser cancelado")

    agendamento.status = 'cancelado'
    agendamento.excluido_por = request.user
    agendamento.excluido_em = datetime.now()
    agendamento.save()

    return 204, None


# --- ROTAS USUÁRIO (Todos autenticados) ---
@user_router.get("/agendamentos", response=List[schemas.AgendamentoOut])
def listar_agendamentos(request, status: str = None, tipo: str = None):
    """
    Lista agendamentos - Filtros opcionais por status e tipo
    """
    queryset = models.Agendamento.objects.all()

    # Filtra por status se fornecido
    if status:
        queryset = queryset.filter(status=status)

    # Filtra por tipo se fornecido
    if tipo:
        queryset = queryset.filter(tipo=tipo)

    # Filtra por armazéns permitidos se não for Master/Admin
    if request.user.tipo not in ["Master", "Admin"]:
        queryset = queryset.filter(
            armazem_id__in=request.user.armazens_permitidos.values_list('id')
        )

    return queryset.order_by('-data_inicio')


@user_router.get("/agendamentos/{agendamento_id}", response=schemas.AgendamentoOut)
def visualizar_agendamento(request, agendamento_id: int):
    """
    Visualiza detalhes de um agendamento específico
    """
    agendamento = get_object_or_404(models.Agendamento, id=agendamento_id)

    # Verifica permissão
    if request.user.tipo not in ["Master", "Admin"]:
        if agendamento.armazem_id not in request.user.armazens_permitidos.values_list('id'):
            raise PermissionDenied("Acesso não autorizado a este agendamento")

    return agendamento


@user_router.get("/agendamentos/proximos", response=List[schemas.AgendamentoOut])
def listar_proximos_agendamentos(request, dias: int = 7):
    """
    Lista agendamentos dos próximos dias (padrão: 7 dias)
    """
    data_inicio = datetime.now()
    data_fim = data_inicio + timedelta(days=dias)

    queryset = models.Agendamento.objects.filter(
        data_inicio__range=[data_inicio, data_fim],
        status__in=['aguardando', 'em_andamento']
    )

    # Filtra por armazéns permitidos se não for Master/Admin
    if request.user.tipo not in ["Master", "Admin"]:
        queryset = queryset.filter(
            armazem_id__in=request.user.armazens_permitidos.values_list('id')
        )

    return queryset.order_by('data_inicio')


@user_router.get("/agendamentos/notificacoes", response=List[schemas.NotificacaoOut])
def listar_notificacoes(request):
    """
    Lista notificações do usuário sobre agendamentos
    """
    # Notificações de agendamentos que o usuário criou ou está relacionado
    return models.NotificacaoAgendamento.objects.filter(
        agendamento__usuario=request.user
    ).order_by('-criada_em')


# Montagem da hierarquia de roteadores
auth_router.add_router("/master", master_router, tags=["Agendamentos-Master"])
auth_router.add_router("/admin", admin_router, tags=["Agendamentos-Admin"])
auth_router.add_router("/user", user_router, tags=["Agendamentos-Usuario"])
router.add_router("", auth_router)