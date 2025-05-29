from datetime import datetime
from typing import Optional
from .models import LogErro
from apps.robos.models import Robo


class LogErroService:
    @staticmethod
    def criar_log(mensagem: str, origem: str, robo_id: Optional[int] = None) -> LogErro:
        """
        Cria um novo log de erro no sistema.
        """
        log_data = {
            'mensagem': mensagem,
            'origem': origem,
        }

        if robo_id:
            log_data['robo_id'] = robo_id

        return LogErro.objects.create(**log_data)

    @staticmethod
    def filtrar_logs(
            origem: Optional[str] = None,
            robo_id: Optional[int] = None,
            data_inicio: Optional[datetime] = None,
            data_fim: Optional[datetime] = None,
            limit: int = 100
    ):
        """
        Filtra logs de erro com base nos parâmetros fornecidos.
        """
        queryset = LogErro.objects.all()

        if origem:
            queryset = queryset.filter(origem__icontains=origem)

        if robo_id:
            queryset = queryset.filter(robo_id=robo_id)

        if data_inicio:
            queryset = queryset.filter(data_hora__gte=data_inicio)

        if data_fim:
            queryset = queryset.filter(data_hora__lte=data_fim)

        return queryset.order_by('-data_hora')[:limit]