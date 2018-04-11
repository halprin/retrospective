from channels.routing import ProtocolTypeRouter, URLRouter
from backend.api import routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': URLRouter(routing.websocket_urlpatterns)
})
