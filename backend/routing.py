from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

import backend.mess.routing as chat_routing
import backend.users.routing as users_routing
import backend.notifications.routing as notifications_routing

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                chat_routing.websocket_urlpatterns + users_routing.websocket_urlpatterns + notifications_routing.websocket_urlpatterns
            )
        ),
    ),
})
