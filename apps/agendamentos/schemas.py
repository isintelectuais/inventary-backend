from ninja import Schema
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum


class StatusAgendamento(str, Enum):
    concluido = "concluido"
    aguardando = "aguardando"
    em_andamento = "em_andamento"
    alerta = "alerta"
    problema = "problema"
    cancelado = "cancelado"


class TipoAgendamento(str, Enum):
    completo = "completo"
    parcial = "parcial"
    emergencial = "emergencial"


class AgendamentoIn(Schema):
    robo_id: int
    armazem_id: int
    tipo: TipoAgendamento
    data_inicio: datetime
    data_fim: datetime
    descricao: Optional[str] = None
    cidades: Optional[List[str]] = None  # Para inventário parcial


class AgendamentoUpdate(Schema):
    status: Optional[StatusAgendamento] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    descricao: Optional[str] = None
    cidades: Optional[List[str]] = None


class AgendamentoOut(Schema):
    id: int
    robo_id: int
    armazem_id: int
    usuario_id: int
    status: StatusAgendamento
    tipo: TipoAgendamento
    data_inicio: datetime
    data_fim: datetime
    descricao: Optional[str] = None
    cidades: List[str] = []
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        orm_mode = True


class NotificacaoOut(Schema):
    id: int
    agendamento_id: int
    mensagem: str
    tipo: str
    lida: bool
    criada_em: datetime

    class Config:
        orm_mode = True


class DashboardAgendamento(Schema):
    status: str
    quantidade: int
    percentual: float


class EstatisticasAgendamento(Schema):
    total: int
    por_status: List[DashboardAgendamento]
    proximos: List[AgendamentoOut]