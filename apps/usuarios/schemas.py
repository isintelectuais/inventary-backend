from pydantic import BaseModel, validator, root_validator, field_validator, model_validator
from typing import Optional

class UsuarioBase(BaseModel):
    nome: str
    email: str
    matricula: Optional[str] = None  # Campo agora opcional
    departamento: str
    cargo: str
    tipo: str  # 'Master', 'Admin', 'Usuario'

class UsuarioCreate(UsuarioBase):
    senha: str
    confirmar_senha: str

    @validator('confirmar_senha')
    def senhas_coincidem(cls, v, values):
        if 'senha' in values and v != values['senha']:
            raise ValueError("As senhas não coincidem")
        return v

class UsuarioOut(UsuarioBase):
    id: int


class AdminCriaUsuarioSchema(BaseModel):
    nome: str
    email: str
    matricula: str
    departamento: str
    cargo: str
    senha: str
    confirmar_senha: str

    @field_validator('*')
    def check_empty_fields(cls, v, info):
        if not v:
            raise ValueError(f"O campo {info.field_name} não pode estar vazio")
        return v

    @field_validator('confirmar_senha')
    def passwords_match(cls, v, info):
        if 'senha' in info.data and v != info.data['senha']:
            raise ValueError("As senhas não coincidem")
        return v

class AlterarSenha(BaseModel):
    senha_atual: str
    nova_senha: str
    confirmar_senha: str

class LoginSchema(BaseModel):
    email: Optional[str] = None
    matricula: Optional[str] = None
    senha: str

    @root_validator(pre=True)
    def verificar_email_ou_matricula(cls, values):
        email = values.get('email')
        matricula = values.get('matricula')

        if not email and not matricula:
            raise ValueError("Email ou matrícula é obrigatório.")
        return values



class AlterarSenha(BaseModel):
    usuario_id: int
    senha_atual: str
    nova_senha: str
    confirmar_senha: str

    @field_validator('*')
    def check_empty_fields(cls, v, info):
        field_name = info.field_name
        if not v and field_name != 'usuario_id':  # usuario_id é int, não checa vazio
            raise ValueError(f"O campo {field_name} não pode estar vazio")
        return v

    @field_validator('confirmar_senha')
    def passwords_match(cls, v, info):
        data = info.data
        if 'nova_senha' in data and v != data['nova_senha']:
            raise ValueError("As senhas não coincidem")
        return v