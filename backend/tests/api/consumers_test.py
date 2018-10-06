from unittest.mock import patch, MagicMock, PropertyMock
from backend.api.consumers import RetrospectiveConsumer
import uuid
from backend.tests.util import retro
import pickle


@patch('backend.api.consumers.async_to_sync', autospec=True)
@patch('backend.api.consumers.RetrospectiveConsumer.accept', autospec=True)
def test_connect_no_subprotocols(mock_accept_function, mock_async_to_sync_function):
    object_under_test = RetrospectiveConsumer({})

    mock_channel_layer = MagicMock()
    mock_group_add = PropertyMock()
    type(mock_channel_layer).group_add = mock_group_add
    object_under_test.channel_layer = mock_channel_layer

    object_under_test.connect()

    mock_group_add.assert_not_called()
    mock_accept_function.assert_not_called()


@patch('backend.api.consumers.async_to_sync', autospec=True)
@patch('backend.api.consumers.RetrospectiveConsumer.accept', autospec=True)
def test_connect_empty_subprotocols(mock_accept_function, mock_async_to_sync_function):
    object_under_test = RetrospectiveConsumer({'subprotocols': []})

    mock_channel_layer = MagicMock()
    mock_group_add = PropertyMock()
    type(mock_channel_layer).group_add = mock_group_add
    object_under_test.channel_layer = mock_channel_layer

    object_under_test.connect()

    mock_group_add.assert_not_called()
    mock_accept_function.assert_not_called()


@patch('backend.api.consumers.async_to_sync', autospec=True)
@patch('backend.api.consumers.RetrospectiveConsumer.accept', autospec=True)
def test_connect_one_subprotocols(mock_accept_function, mock_async_to_sync_function):
    object_under_test = RetrospectiveConsumer({'subprotocols': ['asdf']})

    mock_channel_layer = MagicMock()
    mock_group_add = PropertyMock()
    type(mock_channel_layer).group_add = mock_group_add
    object_under_test.channel_layer = mock_channel_layer

    object_under_test.connect()

    mock_group_add.assert_not_called()
    mock_accept_function.assert_not_called()


@patch('backend.api.consumers.importlib', autospec=True)
@patch('backend.api.consumers.async_to_sync', autospec=True)
@patch('backend.api.consumers.RetrospectiveConsumer.accept', autospec=True)
def test_connect_invalid_token(mock_accept_function, mock_async_to_sync_function, mock_importlib):
    mock_retro_id = uuid.uuid4()

    object_under_test = RetrospectiveConsumer({
        'subprotocols': ['incorrect_user_token', '2'],
        'url_route': {
            'kwargs': {
                'retro_id': mock_retro_id
            }
        }
    })

    mock_channel_layer = MagicMock()
    mock_group_add = PropertyMock()
    type(mock_channel_layer).group_add = mock_group_add
    object_under_test.channel_layer = mock_channel_layer

    mock_service = MagicMock()
    mock_importlib.import_module.return_value.ServiceV2 = mock_service
    mock_service.get_retro.return_value = retro.create_mock_retro(id=str(mock_retro_id), participants=[
        retro.create_mock_participant(token='some_token')])

    object_under_test.connect()

    mock_group_add.assert_not_called()
    mock_accept_function.assert_not_called()


@patch('backend.api.consumers.importlib', autospec=True)
@patch('backend.api.consumers.async_to_sync', autospec=True)
@patch('backend.api.consumers.RetrospectiveConsumer.accept', autospec=True)
def test_connect(mock_accept_function, mock_async_to_sync_function, mock_importlib):
    mock_retro_id = uuid.uuid4()
    mock_user_token = 'user_token'

    object_under_test = RetrospectiveConsumer({
        'subprotocols': [mock_user_token, '2'],
        'url_route': {
            'kwargs': {
                'retro_id': mock_retro_id
            }
        }
    })

    object_under_test.channel_name = 'channel_name'

    mock_channel_layer = MagicMock()
    mock_group_add = PropertyMock()
    type(mock_channel_layer).group_add = mock_group_add
    object_under_test.channel_layer = mock_channel_layer

    mock_service = MagicMock()
    mock_importlib.import_module.return_value.ServiceV2 = mock_service
    mock_service.get_retro.return_value = retro.create_mock_retro(id=str(mock_retro_id), participants=[retro.create_mock_participant(token=mock_user_token)])

    object_under_test.connect()

    mock_group_add.assert_called_once()
    mock_accept_function.assert_called_with(object_under_test, mock_user_token)


@patch('backend.api.consumers.async_to_sync', autospec=True)
def test_disconnect(mock_async_to_sync_function):
    object_under_test = RetrospectiveConsumer({})

    object_under_test.channel_name = 'channel_name'
    object_under_test.retro_id = 'retro_id'

    mock_channel_layer = MagicMock()
    mock_group_discard = PropertyMock()
    type(mock_channel_layer).group_discard = mock_group_discard
    object_under_test.channel_layer = mock_channel_layer

    object_under_test.disconnect(26)

    mock_group_discard.assert_called_once()


def test_receive():
    object_under_test = RetrospectiveConsumer({})

    object_under_test.receive('text')


@patch('backend.api.consumers.pickle', autospec=True)
@patch('backend.api.consumers.json', autospec=True)
@patch('backend.api.consumers.importlib', autospec=True)
def test_disburse_update(mock_importlib, mock_json_module, mock_pickle_module):
    object_under_test = RetrospectiveConsumer({})

    object_under_test.user_token = 'user_token'
    object_under_test.version = '2'
    object_under_test.send = MagicMock()

    mock_service = MagicMock()
    mock_importlib.import_module.return_value.ServiceV2 = mock_service

    object_under_test.disburse_update({
        'retro': retro.create_mock_retro()
    })

    mock_service.sanitize_retro_for_user_and_step.assert_called_once()
    object_under_test.send.assert_called_once()
