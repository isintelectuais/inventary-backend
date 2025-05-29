from django.urls import re_path
from apps.robos import consumers

websocket_urlpatterns = [
    re_path(r'ws/robos/(?P<robo_id>\w+)/$', consumers.RoboConsumer.as_asgi()),
]