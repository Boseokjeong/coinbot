# coinbot/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import coinbot.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coinbot.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # 여기서 coinbot/routing.py에서 websocket_urlpatterns를 정의해야 합니다.
    "websocket": AuthMiddlewareStack(
        URLRouter(
            coinbot.routing.websocket_urlpatterns
        )
    ),
})
