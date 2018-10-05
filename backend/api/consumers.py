import importlib
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from backend.api import token
import json
import pickle


class RetrospectiveConsumer(WebsocketConsumer):
    def connect(self):
        if 'subprotocols' not in self.scope or len(self.scope['subprotocols']) < 2:
            # do not accept the connection
            return

        self.retro_id = str(self.scope['url_route']['kwargs']['retro_id'])
        self.user_token = self.scope['subprotocols'][0]
        self.version = self.scope['subprotocols'][1]

        # TODO: support version 2
        retro = self._get_service(self.version).get_retro(self.retro_id)

        if not token.token_is_valid(self.user_token, retro):
            # do not accept the connection
            return

        async_to_sync(self.channel_layer.group_add)(self.retro_id, self.channel_name)

        self.accept(self.user_token)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.retro_id, self.channel_name)

    def receive(self, text_data):
        # do nothing
        pass

    def disburse_update(self, event):
        retro = pickle.loads(event['retro'])

        sanitized_retro = self._get_service(self.version).sanitize_retro_for_user_and_step(retro, self.user_token)

        self.send(text_data=json.dumps(sanitized_retro))

    @staticmethod
    def _get_service(version: str):
        service_version = 'V' + version if version != '1' else ''

        module = importlib.import_module('..service{}'.format(service_version), __name__)
        class_to_use = getattr(module, 'Service{}'.format(service_version))

        return class_to_use
