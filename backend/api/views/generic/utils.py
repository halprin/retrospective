import importlib
from dataclasses import dataclass
import json
from typing import Dict


@dataclass
class Request:
    body: str
    path_values: Dict[str, str]
    headers: Dict[str, str]


@dataclass
class Response:
    statusCode: int
    body: str
    headers: Dict[str, str]


class Lambda:
    @staticmethod
    def _get_request_http_headers(event: dict):
        return event['headers']

    @staticmethod
    def _get_request_body(event: dict):
        return event['body']

    @staticmethod
    def _get_request_path_values(event: dict):
        return event['pathParameters']

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
            'statusCode': response.statusCode,
            'headers': response.headers
        }


def get_service_version(request_details: Request):
    api_version = request_details.headers.get('Api-Version', '1')

    service_version = 'V' + api_version if api_version != '1' else ''

    return service_version


def find_class_and_method_to_call(service_version: str, generic_class_name: str, method_name: str):
    class_name = generic_class_name[len('Generic'):]
    module = importlib.import_module('...views{}'.format(service_version), __name__)
    class_to_use = getattr(module, '{}{}'.format(class_name, service_version))
    method_to_call = getattr(class_to_use, method_name)

    return class_to_use, method_to_call


class VersionServiceView:
    @staticmethod
    def service():
        raise NotImplementedError
