# routing.py
from django.urls import path
from trading import consumers

websocket_urlpatterns = [
    path('ws/ticker/', consumers.TickerConsumer.as_asgi()),
]