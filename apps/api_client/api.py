from ninja import Router
from django.http import HttpRequest
from datetime import datetime
from typing import List, Optional
from ninja.errors import HttpError

from .models import ApiToken, ApiChecklist
from .schemas import (
    WebhookPayload,
    ChecklistResponse,
    NovoTokenSchema,
    NovoTokenResponse,
    ApiChecklistSchema
)
from .services import processar_webhook
from apps.usuarios.authentication import JWTAuth  # sua autenticação personalizada

api = Router(tags=["WMS API"])

# 🔓 Rota pública com token do WMS (não usa JWTAuth)
@api.post("/webhook", response=ChecklistResponse)
def receber_dados(request: HttpRequest, payload: WebhookPayload):
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HttpError(401, "Token não fornecido")

    token = token.replace("Bearer ", "")
    if not ApiToken.objects.filter(token=token, ativo=True, expiracao__gte=datetime.now()).exists():
        raise HttpError(403, "Token inválido ou expirado")

    resultado = processar_webhook(payload.dict(), token=token)
    return resultado


# 🔐 Rota protegida: apenas Admin/Master podem cadastrar tokens
@api.post("/tokens", response=NovoTokenResponse, auth=JWTAuth())
def criar_token(request, payload: NovoTokenSchema):
    user = request.auth
    if not hasattr(user, 'tipo') or user.tipo not in ["Admin", "Master"]:
        raise HttpError(403, "Permissão negada: apenas Admin ou Master.")

    if ApiToken.objects.filter(token=payload.token).exists():
        raise HttpError(400, "Token já existe")

    novo_token = ApiToken.objects.create(
        token=payload.token,
        expiracao=payload.expiracao,
        ativo=True
    )

    return {
        "status": "Token criado com sucesso",
        "id": novo_token.id,
        "expiracao": novo_token.expiracao
    }

# 🔐 Rota protegida: apenas Admin/Master podem visualizar checklists
@api.get("/checklists", response=List[ApiChecklistSchema], auth=JWTAuth())
def listar_checklists(
    request,
    referencia: Optional[str] = None,
    entidade: Optional[str] = None,
    divergente: Optional[bool] = None
):
    user = request.auth
    if not hasattr(user, 'tipo') or user.tipo not in ["Admin", "Master"]:
        raise HttpError(403, "Permissão negada: apenas Admin ou Master.")

    qs = ApiChecklist.objects.all()

    if referencia:
        qs = qs.filter(referencia_externa__icontains=referencia)

    if entidade:
        qs = qs.filter(entidade=entidade)

    if divergente is not None:
        if divergente:
            qs = qs.exclude(divergencia__isnull=True).exclude(divergencia="")
        else:
            qs = qs.filter(divergencia__isnull=True) | qs.filter(divergencia="")

    return qs.order_by("-data_hora")[:100]
