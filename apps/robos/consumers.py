import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from apps.robos.models import Robo


class RoboConsumer(AsyncWebsocketConsumer):
    groups = ["robos_monitor"]

    async def connect(self):
        self.robo_id = self.scope['url_route']['kwargs']['robo_id']

        # Autenticação do robô via token
        try:
            await self.authenticate_robo()
            await self.accept()

            # Adiciona à group específica do robô
            await self.channel_layer.group_add(
                f"robo_{self.robo_id}",
                self.channel_name
            )

        except Exception as e:
            await self.close(code=4001)
            print(f"Conexão rejeitada: {str(e)}")

    @database_sync_to_async
    def authenticate_robo(self):
        """Verifica se o robô existe e é válido"""
        robo = Robo.objects.get(id=self.robo_id)
        if not robo.habilitado:
            raise PermissionError("Robô desabilitado")
        return robo

    async def disconnect(self, close_code):
        # Remove do group ao desconectar
        await self.channel_layer.group_discard(
            f"robo_{self.robo_id}",
            self.channel_name
        )

    async def receive(self, text_data):
        """Recebe mensagens do robô"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'status_update':
                await self.handle_status_update(data)
            elif message_type == 'log_error':
                await self.handle_log_error(data)
            # Adicione outros tipos de mensagem conforme necessário

        except json.JSONDecodeError:
            await self.send(json.dumps({
                'error': 'Invalid JSON format'
            }))

    @database_sync_to_async
    def handle_status_update(self, data):
        """Atualiza status do robô no banco de dados"""
        Robo.objects.filter(id=self.robo_id).update(
            status=data.get('status'),
            sensores=data.get('sensores', {})
        )

    @database_sync_to_async
    def handle_log_error(self, data):
        """Registra erro do robô"""
        from logs_erro.models import LogErro
        LogErro.objects.create(
            robo_id=self.robo_id,
            mensagem=data.get('message'),
            origem=data.get('origin', 'websocket')
        )

    async def send_command(self, event):
        """Envia comando para o robô"""
        await self.send(text_data=json.dumps(event['data']))