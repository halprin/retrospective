from django.urls import path
from backend.api.consumers import RetrospectiveConsumer

websocket_urlpatterns = [
    path('api/ws/<uuid:retro_id>', RetrospectiveConsumer),
]
