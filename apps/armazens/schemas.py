from typing import Optional
from datetime import datetime
from ninja import Schema
from pydantic import field_validator, ValidationInfo


class ArmazemIn(Schema):
    codigo_armazem: str
    nome: str

    qtd_niveis: str
    qtd_cidades: int
    qtd_bairros_por_cidade: int
    qtd_ruas_por_bairro: int
    qtd_predios_por_rua: int

    @field_validator('*', mode="before")
    @classmethod
    def check_empty(cls, v, info: ValidationInfo):
        """Valida se os campos não estão vazios (para strings)."""
        if v is None or (isinstance(v, str) and not v.strip()):
            raise ValueError(f"O campo '{info.field_name}' não pode ser vazio.")
        return v

    @field_validator('qtd_cidades', 'qtd_bairros_por_cidade', 'qtd_ruas_por_bairro', 'qtd_predios_por_rua', mode="before")
    @classmethod
    def check_positive(cls, v, info: ValidationInfo):
        """Valida se os campos numéricos não são negativos."""
        if isinstance(v, int) and v < 0:
            raise ValueError(f"O campo '{info.field_name}' não pode ter valores negativos.")
        return v


class ArmazemOut(Schema):
    id: int
    codigo_armazem: str
    nome: str

    qtd_niveis: str
    qtd_cidades: int
    qtd_bairros_por_cidade: int
    qtd_ruas_por_bairro: int
    qtd_predios_por_rua: int

    codigo_barra: str
    criado_em: datetime
    atualizado_em: datetime
    ativo: bool


class ArmazemUpdate(Schema):
    nome: Optional[str] = None
    qtd_niveis: Optional[str] = None
    qtd_cidades: Optional[int] = None
    qtd_bairros_por_cidade: Optional[int] = None
    qtd_ruas_por_bairro: Optional[int] = None
    qtd_predios_por_rua: Optional[int] = None
