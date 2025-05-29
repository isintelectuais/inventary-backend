from ninja import Router
from django.shortcuts import get_object_or_404
from typing import List
from ninja.errors import HttpError
from . import schemas, models
from apps.usuarios.authentication import JWTAuth

router = Router()
auth_router = Router(auth=JWTAuth())
robo_router = Router()


# --- Rotas Autenticadas ---
@auth_router.get("/lista-trajetorias", response=List[schemas.TrajetoriaOut])
def listar_trajetorias(request, agendamento_id: int = None):
    queryset = models.Trajetoria.objects.all()

    if agendamento_id:
        queryset = queryset.filter(agendamento_id=agendamento_id)

    return queryset.order_by('-data_hora')


@auth_router.get("/{trajetoria_id}", response=schemas.TrajetoriaCompletaOut)
def detalhes_trajetoria(request, trajetoria_id: int):
    trajetoria = get_object_or_404(models.Trajetoria, id=trajetoria_id)
    return trajetoria


# --- Rotas Robô (comunicação direta) ---
@robo_router.post("/registrar", response={201: schemas.TrajetoriaOut})
def registrar_trajetoria(request, payload: schemas.TrajetoriaIn):
    try:
        trajetoria = models.Trajetoria.objects.create(
            agendamento_id=payload.agendamento_id,
            codigo_localizacao=payload.codigo_localizacao,
            dados_sensores=payload.dados_sensores
        )
        return 201, trajetoria
    except Exception as e:
        raise HttpError(400, str(e))


@robo_router.post("/{trajetoria_id}/ponto", response={201: schemas.PontoInteresseOut})
def registrar_ponto_interesse(request, trajetoria_id: int, payload: schemas.PontoInteresseIn):
    trajetoria = get_object_or_404(models.Trajetoria, id=trajetoria_id)

    ponto = models.PontoInteresse.objects.create(
        trajetoria=trajetoria,
        codigo=payload.codigo,
        tipo=payload.tipo,
        dados=payload.dados,
        data_hora=payload.data_hora
    )
    return 201, ponto


# Montagem da hierarquia
auth_router.add_router("/robo", robo_router, tags=["Trajetórias-Robô"])
router.add_router("", auth_router)