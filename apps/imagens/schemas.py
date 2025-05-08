from ninja import Schema
from datetime import datetime


class ImagemOut(Schema):
    id: int
    robo_id: int
    url_imagem: str
    codigo_lido: str
    data_hora: datetime

    class Config:
        orm_mode = True