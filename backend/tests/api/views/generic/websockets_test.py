import os
from backend.api.views.generic import websockets


def test_no_api_version():
    os.environ['ALLOWED_HOST'] = 'DogCow'
    event = {
        'queryStringParameters': {
        },
        'requestContext': {
            'connectionId': 'moof'
        }
    }

    response = websockets.websocket_connect(event, {})

    assert response['statusCode'] == 400
    assert response['body'] == 'Supply an API version'

    event['queryStringParameters']['version'] = ''

    response = websockets.websocket_connect(event, {})

    assert response['statusCode'] == 400
    assert response['body'] == 'Supply an API version'


def test_no_retro_id():
    os.environ['ALLOWED_HOST'] = 'DogCow'
    event = {
        'queryStringParameters': {
            'version': '2'
        },
        'requestContext': {
            'connectionId': 'moof'
        }
    }

    response = websockets.websocket_connect(event, {})

    assert response['statusCode'] == 400
    assert response['body'] == 'Supply a UUID for the retro ID'

    event['queryStringParameters']['uuid'] = ''

    response = websockets.websocket_connect(event, {})

    assert response['statusCode'] == 400
    assert response['body'] == 'Supply a UUID for the retro ID'
