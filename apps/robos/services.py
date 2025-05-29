from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_command_to_robo(robo_id, command, data=None):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"robo_{robo_id}",
        {
            'type': 'send_command',
            'data': {
                'command': command,
                **(data or {})
            }
        }
    )