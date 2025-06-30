from .models import ApiChecklist, ApiLogs, ApiToken
from datetime import datetime
from apps.inventario.models import Inventario

def processar_webhook(dados: dict, token: str):
    codigo_palete = dados.get("codigo_palete")
    encontrado = Inventario.objects.filter(codigo_palete=codigo_palete).exists()
    divergencia = None if encontrado else "Palete não encontrado localmente"

    token_obj = ApiToken.objects.filter(token=token).first()

    log = ApiLogs.objects.create(
        token=token_obj,
        endpoint="/webhook",
        metodo="POST",
        status_http=200,
        sucesso=True,
        payload_enviado={},
        payload_resposta=dados,
        mensagem=divergencia or "Verificação OK",
        data_hora=datetime.now()
    )

    ApiChecklist.objects.create(
        api_log=log,
        referencia_externa=codigo_palete,
        entidade="palete",
        encontrado_localmente=encontrado,
        divergencia=divergencia,
        data_hora=datetime.now()
    )

    return {
        "verificado": True,
        "divergencia": divergencia
    }
