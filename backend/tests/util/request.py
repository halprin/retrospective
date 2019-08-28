from backend.api.views.generic.utils import Request
import json


def create_mock_request(request_body=None, token=None, api_version=None, retro_id=None, issue_id=None, group_id=None) -> Request:

    request = Request(body='', path_values={}, headers={})

    if isinstance(request_body, dict):
        request.body = json.dumps(request_body)
    elif isinstance(request_body, str):
        request.body = request_body

    if token is not None:
        request.headers['Authorization'] = 'Bearer {}'.format(token)

    if api_version is not None:
        request.headers['Api-Version'] = api_version

    if retro_id is not None:
        request.path_values['retro_id'] = retro_id

    if issue_id is not None:
        request.path_values['issue_id'] = issue_id

    if group_id is not None:
        request.path_values['group_id'] = group_id

    return request
