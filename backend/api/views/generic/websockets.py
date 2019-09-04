from . import utils
from .utils import Lambda, Response, exception_to_error_response
from ... import token
from pynamodb.models import Model


@exception_to_error_response
def websocket_connect(event, context):
    query_parameters = event['queryStringParameters']
    retro_id = query_parameters.get('uuid')
    user_token = query_parameters.get('token')
    api_version = query_parameters.get('version')

    connection_id = event['requestContext']['connectionId']

    if api_version is None or len(api_version) == 0:
        return Lambda.get_response(Response(400, 'Supply an API version', {}))

    if retro_id is None or len(retro_id) == 0:
        return Lambda.get_response(Response(400, 'Supply a UUID for the retro ID', {}))

    try:
        retro = utils.get_service(api_version).get_retro(retro_id)
    except Model.DoesNotExist:
        return Lambda.get_response(Response(404, 'retro not found', {}))

    participant = token.get_participant(user_token, retro)
    if participant is None:
        return Lambda.get_response(Response(401, '', {}))

    token.add_connection_id(retro, participant, connection_id)

    successful_connection = Response(200, '', {})
    return Lambda.get_response(successful_connection)
