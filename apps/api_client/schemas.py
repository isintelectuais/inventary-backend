from pydantic import BaseModel, Field
from typing import Optional, Literal, Any
from datetime import datetime

class WebhookPayload(BaseModel):
    codigo_palete: str
    outros_dados: Optional[Any] = None  # Se tiver mais campos no JSON

class ChecklistResponse(BaseModel):
    verificado: bool
    divergencia: Optional[str] = None

class ApiLogSchema(BaseModel):
    id: int
    endpoint: str
    metodo: str
    status_http: int
    sucesso: bool
    mensagem: Optional[str]
    data_hora: datetime

    class Config:
        orm_mode = True

class ApiChecklistSchema(BaseModel):
    id: int
    referencia_externa: str
    entidade: str
    encontrado_localmente: bool
    divergencia: Optional[str]
    data_hora: datetime

    class Config:
        orm_mode = True


class NovoTokenResponse(BaseModel):
    status: str
    id: int
    expiracao: datetime

class NovoTokenSchema(BaseModel):
    token: str = Field(..., example="wms-abc-123")
    expiracao: datetime = Field(..., example="2025-12-31T23:59:59")