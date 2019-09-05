import inspect
from . import utils
from .utils import Lambda, Request, Response, exception_to_error_response, log_response


@log_response
@exception_to_error_response
def add(event, context):
    request = Lambda.get_request(event)
    response = GenericRetroIssueView.post(request)

    return Lambda.get_response(response)


@log_response
@exception_to_error_response
def vote_or_group(event, context):
    request = Lambda.get_request(event)
    response = GenericRetroIssueView.put(request)

    return Lambda.get_response(response)


@log_response
@exception_to_error_response
def delete(event, context):
    request = Lambda.get_request(event)
    response = GenericRetroIssueView.delete(request)

    return Lambda.get_response(response)


class GenericRetroIssueView:
    @classmethod
    def post(cls, request: Request) -> Response:
        service_version = utils.get_service_version(request)

        class_name = cls.__name__
        this_method = inspect.currentframe().f_code.co_name
        class_to_use, method_to_call = utils.find_class_and_method_to_call(service_version, class_name, this_method)

        return method_to_call(class_to_use, request)

    @classmethod
    def put(cls, request: Request) -> Response:
        service_version = utils.get_service_version(request)

        class_name = cls.__name__
        this_method = inspect.currentframe().f_code.co_name
        class_to_use, method_to_call = utils.find_class_and_method_to_call(service_version, class_name, this_method)

        return method_to_call(class_to_use, request)

    @classmethod
    def delete(cls, request: Request) -> Response:
        service_version = utils.get_service_version(request)

        class_name = cls.__name__
        this_method = inspect.currentframe().f_code.co_name
        class_to_use, method_to_call = utils.find_class_and_method_to_call(service_version, class_name, this_method)

        return method_to_call(class_to_use, request)
