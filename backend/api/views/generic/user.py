import inspect
from . import utils
from .utils import Lambda, Request, Response, exception_to_error_response
import logging


@exception_to_error_response
def add_participant(event, context):
    request = Lambda.get_request(event)
    response = GenericRetroUserView.post(request)

    return Lambda.get_response(response)


@exception_to_error_response
def mark_as_ready(event, context):
    logging.warning('Marking a user as ready')
    request = Lambda.get_request(event)
    logging.warning('Got the request')
    response = GenericRetroUserView.put(request)

    return Lambda.get_response(response)


class GenericRetroUserView:
    @classmethod
    def post(cls, request: Request) -> Response:
        service_version = utils.get_service_version(request)

        class_name = cls.__name__
        this_method = inspect.currentframe().f_code.co_name
        class_to_use, method_to_call = utils.find_class_and_method_to_call(service_version, class_name, this_method)

        return method_to_call(class_to_use, request)

    @classmethod
    def put(cls, request: Request) -> Response:
        logging.warning('In GenericRetroUserView put')
        service_version = utils.get_service_version(request)
        logging.warning('Done getting service_version')

        class_name = cls.__name__
        logging.warning('Got the class name')
        this_method = inspect.currentframe().f_code.co_name
        logging.warning('Got the method')
        class_to_use, method_to_call = utils.find_class_and_method_to_call(service_version, class_name, this_method)

        logging.warning('Calling method_to_call')
        return method_to_call(class_to_use, request)
