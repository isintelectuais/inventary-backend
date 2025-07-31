import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_sia.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from sistema_sia.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns())  # <-- note os parênteses
    ),
})
