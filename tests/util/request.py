from unittest.mock import MagicMock


def create_mock_request(token):
    request = MagicMock()

    request.META = {'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)}

    return request
