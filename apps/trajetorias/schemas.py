from ninja import Schema
from datetime import datetime
from typing import List, Dict, Any


class TrajetoriaIn(Schema):
    agendamento_id: int
    codigo_localizacao: str  # cidade:bairro:rua:predio:nivel:apto
    dados_sensores: Dict[str, Any]


class PontoInteresseIn(Schema):
    codigo: str
    tipo: str
    dados: Dict[str, Any]
    data_hora: datetime


class TrajetoriaOut(Schema):
    id: int
    agendamento_id: int
    codigo_localizacao: str
    data_hora: datetime

    class Config:
        orm_mode = True


class PontoInteresseOut(Schema):
    id: int
    trajetoria_id: int
    codigo: str
    tipo: str
    data_hora: datetime

    class Config:
        orm_mode = True


class TrajetoriaCompletaOut(TrajetoriaOut):
    pontos_interesse: List[PontoInteresseOut]