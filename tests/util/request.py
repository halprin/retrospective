from unittest.mock import MagicMock
import json


def create_mock_request(request_body=None, token=None):
    request = MagicMock()

    if request_body is None:
        request.body = ''
    elif isinstance(request_body, dict):
        request.body = json.dumps(request_body)
    elif isinstance(request_body, str):
        request.body = request_body
    else:
        raise TypeError('request_body is neither a dict nor a str')

    if token is not None:
        request.META = {'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)}

    return request
