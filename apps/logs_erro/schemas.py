from datetime import datetime
from typing import Optional
from ninja import Schema
from ninja.orm import create_schema
from .models import LogErro

class LogErroCreate(Schema):
    mensagem: str
    origem: str
    robo_id: Optional[int] = None

LogErroSchema = create_schema(
    LogErro,
    name='LogErroSchema',
    exclude=['id'],
    custom_fields=[
        ('id', int, None),
        ('robo_id', Optional[int], None),
    ]
)

class LogErroFilter(Schema):
    origem: Optional[str] = None
    robo_id: Optional[int] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None