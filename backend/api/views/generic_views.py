from typing import Any
from django.http import HttpRequest
from django.views import View
import inspect
import importlib


def get_service_version(request: HttpRequest):
    api_version = request.META.get('HTTP_API_VERSION', '1')

    service_version = api_version if api_version != '1' else ''

    return service_version


def find_class_and_method_to_call(service_version: str, method_name: str):
    module = importlib.import_module('..views{}'.format(service_version), __name__)
    class_to_use = getattr(module, 'RetroView{}'.format(service_version))
    method_to_call = getattr(class_to_use, method_name)

    return class_to_use, method_to_call


class GenericRetroView(View):
    def post(self, request: HttpRequest, *args, **kwargs) -> Any:
        service_version = get_service_version(request)

        this_method = inspect.currentframe().f_code.co_name
        class_to_use, method_to_call = find_class_and_method_to_call(service_version, this_method)

        return method_to_call(class_to_use, request, *args, **kwargs)

    def put(self, request: HttpRequest, *args, **kwargs) -> Any:
        service_version = get_service_version(request)

        this_method = inspect.currentframe().f_code.co_name
        class_to_use, method_to_call = find_class_and_method_to_call(service_version, this_method)

        return method_to_call(class_to_use, request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs) -> Any:
        service_version = get_service_version(request)

        this_method = inspect.currentframe().f_code.co_name
        class_to_use, method_to_call = find_class_and_method_to_call(service_version, this_method)

        return method_to_call(class_to_use, request, *args, **kwargs)
