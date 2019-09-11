import importlib
from dataclasses import dataclass
from typing import Dict
from functools import wraps
import traceback
import os
import logging


@dataclass
class Request:
    body: str
    path_values: Dict[str, str]
    headers: Dict[str, str]


@dataclass
class Response:
    status_code: int
    body: str
    headers: Dict[str, str]


class Lambda:
    @staticmethod
    def _get_request_http_headers(event: dict):
        return event.get('headers', {})

    @staticmethod
    def _get_request_body(event: dict):
        return event.get('body', '')

    @staticmethod
    def _get_request_path_values(event: dict):
        return event.get('pathParameters', {})

    @classmethod
    def get_request(cls, event) -> Request:
        body = cls._get_request_body(event)
        path_values = cls._get_request_path_values(event)
        headers = cls._get_request_http_headers(event)

        return Request(body, path_values, headers)

    @classmethod
    def get_response(cls, response: Response) -> dict:
        return {
            'body': response.body,
            'statusCode': response.status_code,
            'headers': {**response.headers, 'Access-Control-Allow-Origin': 'https://{}'.format(os.environ['ALLOWED_HOST'])}
        }


def get_service_version(request_details: Request):
    api_version = request_details.headers.get('Api-Version', request_details.headers.get('api-version', '1'))

    service_version = 'V' + api_version if api_version != '1' else ''

    return service_version


def find_class_and_method_to_call(service_version: str, generic_class_name: str, method_name: str):
    class_name = generic_class_name[len('Generic'):]
    module = importlib.import_module('...views{}'.format(service_version), __name__)
    class_to_use = getattr(module, '{}{}'.format(class_name, service_version))
    method_to_call = getattr(class_to_use, method_name)

    return class_to_use, method_to_call


def get_service(version: str):
    service_version = 'V' + version if version != '1' else ''

    module = importlib.import_module('....service{}'.format(service_version), __name__)
    class_to_use = getattr(module, 'Service{}'.format(service_version))

    return class_to_use


def exception_to_error_response(original_function):
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        try:
            return original_function(*args, **kwargs)
        except Exception:
            context = args[1]
            logging.error('Exception during execution of {}'.format(original_function))
            traceback.print_exc()
            response = Response(500, 'An unexpected error occurred. Reference {}'.format(
                context.aws_request_id), {'Content-Type': 'text/plain'})
            return Lambda.get_response(response)

    return wrapper


def log_response(original_function):
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        response = original_function(*args, **kwargs)
        logging.info('Responding to {} with status {}'.format(original_function, response['statusCode']))
        if 400 <= response['statusCode'] <= 599:
            logging.warning('Response body: {}'.format(response['body']))
        return response

    return wrapper


class VersionServiceView:
    @staticmethod
    def service():
        raise NotImplementedError
