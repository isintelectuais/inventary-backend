import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ImagemCapturada
from django.utils.timezone import now
from django.db import IntegrityError

class ImagemConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({"status": "connected"}))

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            # Dados esperados
            codigo_lido = data.get("codigo_lido")
            robo_id = data.get("robo_id")

            if not codigo_lido or not robo_id:
                await self.send(text_data=json.dumps({
                    "status": "error",
                    "message": "Campos 'codigo_lido' e 'robo_id' são obrigatórios."
                }))
                return

            imagem = ImagemCapturada.objects.create(
                codigo_lido=codigo_lido,
                robo_id=robo_id,
                data_hora=now()
            )

            await self.send(text_data=json.dumps({
                "status": "success",
                "message": "Imagem registrada com sucesso.",
                "imagem_id": imagem.id
            }))

        except IntegrityError:
            await self.send(text_data=json.dumps({
                "status": "error",
                "message": "Erro ao salvar imagem no banco de dados."
            }))

        except Exception as e:
            await self.send(text_data=json.dumps({
                "status": "error",
                "message": str(e)
            }))

    async def disconnect(self, close_code):
        await self.send(text_data=json.dumps({"status": "disconnected"}))
