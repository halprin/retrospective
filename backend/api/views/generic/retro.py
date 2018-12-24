import inspect
from . import utils
from .utils import Lambda, Request, Response


def create(event, context):
    request = Lambda.get_request(event)
    response = GenericRetroView.post(request)

    return Lambda.get_response(response)


def move(event, context):
    request = Lambda.get_request(event)
    response = GenericRetroView.put(request)

    return Lambda.get_response(response)


def get(event, context):
    request = Lambda.get_request(event)
    response = GenericRetroView.get(request)

    return Lambda.get_response(response)


class GenericRetroView:
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
    def get(cls, request: Request) -> Response:
        service_version = utils.get_service_version(request)

        class_name = cls.__name__
        this_method = inspect.currentframe().f_code.co_name
        class_to_use, method_to_call = utils.find_class_and_method_to_call(service_version, class_name, this_method)

        return method_to_call(class_to_use, request)
