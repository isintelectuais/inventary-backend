from ninja import Schema
from datetime import datetime
from typing import List, Optional


class InventarioIn(Schema):
    agendamento_id: int
    codigo_palete: str
    codigo_endereco: str


class InventarioOut(Schema):
    id: int
    agendamento_id: int
    codigo_palete: str
    codigo_endereco: str
    data_hora: datetime

    class Config:
        orm_mode = True


class EstatisticasInventario(Schema):
    total_armazens: int
    total_registros: int
    ultimo_inventario: Optional[datetime]


class DashboardArmazem(Schema):
    armazem: str
    total_itens: int
    ultimo_registro: Optional[datetime]


class DashboardInventario(Schema):
    armazens: List[DashboardArmazem]