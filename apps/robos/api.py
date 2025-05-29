from ninja import Router
from django.shortcuts import get_object_or_404
from typing import List
from ninja.errors import HttpError
from django.core.exceptions import PermissionDenied
from . import schemas, models
from apps.usuarios.authentication import JWTAuth

router = Router()
auth_router = Router(auth=JWTAuth())

# Sub-roteadores
master_router = Router(auth=JWTAuth())
admin_router = Router(auth=JWTAuth())
robo_router = Router(auth=JWTAuth())  # Para comunicação direta do robô


# --- Rotas Master ---
@master_router.post("/", response={201: schemas.RoboOut})
def criar_robo(request, payload: schemas.RoboIn):
    if request.user.tipo != "Master":
        raise PermissionDenied("Acesso restrito a usuários Master")

    robo = models.Robo.objects.create(**payload.dict())
    return 201, robo


# --- Rotas Admin ---
@admin_router.get("/", response=List[schemas.RoboOut])
def listar_robos(request, armazem_id: int = None):
    queryset = models.Robo.objects.all()

    if armazem_id:
        queryset = queryset.filter(armazem_id=armazem_id)

    if request.user.tipo == "Admin":
        queryset = queryset.filter(armazem__in=request.user.armazens_permitidos.all())

    return queryset


@admin_router.post("/{robo_id}/comando", response={201: schemas.ComandoOut})
def enviar_comando(request, robo_id: int, payload: schemas.ComandoIn):
    robo = get_object_or_404(models.Robo, id=robo_id)

    if request.user.tipo == "Admin":
        if robo.armazem not in request.user.armazens_permitidos.all():
            raise PermissionDenied("Acesso não autorizado a este robô")

    comando = models.ComandoRobo.objects.create(
        robo=robo,
        tipo=payload.tipo,
        usuario=request.user
    )
    return 201, comando


# --- Rotas Robô (comunicação direta) ---
@robo_router.post("/{identificador}/status", response={200: dict})
def atualizar_status_robo(request, identificador: str, payload: schemas.SensorData):
    try:
        robo = models.Robo.objects.get(identificador=identificador)
        robo.sensores = payload.dict()
        robo.status = 'ativo' if payload.bateria and payload.bateria > 5 else 'inativo'
        robo.save()
        return 200, {"status": "success"}
    except Exception as e:
        raise HttpError(400, str(e))


@robo_router.get("/{identificador}/comandos", response=List[schemas.ComandoOut])
def obter_comandos(request, identificador: str):
    robo = get_object_or_404(models.Robo, identificador=identificador)
    return robo.comandos.filter(executado=False)


# Montagem da hierarquia
auth_router.add_router("/master", master_router, tags=["Robôs-Master"])
auth_router.add_router("/admin", admin_router, tags=["Robôs-Admin"])
auth_router.add_router("/robo", robo_router, tags=["Robôs-Comunicação"])
router.add_router("", auth_router)