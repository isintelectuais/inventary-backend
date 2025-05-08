from ninja import Schema
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class StatusRobo(str, Enum):
    ativo = "ativo"
    inativo = "inativo"
    em_missao = "em_missao"
    manutencao = "manutencao"
    erro = "erro"


class TipoComando(str, Enum):
    desligar = "desligar"
    reiniciar = "reiniciar"
    pausar = "pausar"
    retomar = "retomar"
    emergencia = "emergencia"


class RoboIn(Schema):
    identificador: str
    armazem_id: int
    modelo: str
    configuracao: Dict[str, Any]


class RoboUpdate(Schema):
    status: Optional[StatusRobo] = None
    habilitado: Optional[bool] = None
    configuracao: Optional[Dict[str, Any]] = None


class RoboOut(Schema):
    id: int
    identificador: str
    armazem_id: int
    modelo: str
    status: StatusRobo
    habilitado: bool
    ultima_comunicacao: datetime
    configuracao: Dict[str, Any]

    class Config:
        orm_mode = True


class ComandoIn(Schema):
    tipo: TipoComando


class ComandoOut(Schema):
    id: int
    robo_id: int
    tipo: TipoComando
    executado: bool
    data_criacao: datetime

    class Config:
        orm_mode = True


class SensorData(Schema):
    temperatura: Optional[float] = None
    bateria: Optional[float] = None
    velocidade: Optional[float] = None
    obstaculo_detectado: Optional[bool] = None