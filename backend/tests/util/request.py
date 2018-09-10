from unittest.mock import MagicMock
import json


def create_mock_request(request_body=None, token=None, api_version=None):
    request = MagicMock()

    if request_body is None:
        request.body = ''
    elif isinstance(request_body, dict):
        request.body = json.dumps(request_body)
    elif isinstance(request_body, str):
        request.body = request_body
    else:
        raise TypeError('request_body is neither a dict nor a str')

    meta_dict = {}

    if token is not None:
        meta_dict['HTTP_AUTHORIZATION'] = 'Bearer {}'.format(token)

    if api_version is not None:
        meta_dict['HTTP_API_VERSION'] = api_version

    request.META = meta_dict

    return request
