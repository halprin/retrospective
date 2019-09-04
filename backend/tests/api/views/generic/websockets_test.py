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

    assert 400 == response['statusCode']
    assert 'Supply an API version' == response['body']

    event['queryStringParameters']['version'] = ''

    response = websockets.websocket_connect(event, {})

    assert 400 == response['statusCode']
    assert 'Supply an API version' == response['body']


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

    assert 400 == response['statusCode']
    assert 'Supply a UUID for the retro ID' == response['body']

    event['queryStringParameters']['uuid'] = ''

    response = websockets.websocket_connect(event, {})

    assert 400 == response['statusCode']
    assert 'Supply a UUID for the retro ID' == response['body']
