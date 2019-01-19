from . import utils
from .utils import Lambda, Response, exception_to_error_response
from ... import token
from pynamodb.models import Model


@exception_to_error_response
def websocket_connect(event, context):
    query_parameters = event['queryStringParameters']
    retro_id = query_parameters['uuid']
    user_token = query_parameters['token']
    api_version = query_parameters['version']

    connection_id = event['requestContext']['connectionId']

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
