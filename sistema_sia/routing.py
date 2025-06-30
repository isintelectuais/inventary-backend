from django.urls import re_path
from apps.robos.consumers import RoboConsumer
from apps.imagens.consumers import ImagemConsumer

websocket_urlpatterns = [
    re_path(r'ws/robos/(?P<robo_id>\w+)/$', RoboConsumer.as_asgi()),
    re_path(r'ws/imagens/$', ImagemConsumer.as_asgi())
]