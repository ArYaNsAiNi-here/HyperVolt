"""
WebSocket routing configuration.
"""
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/sensors/', consumers.SensorConsumer.as_asgi()),
]
