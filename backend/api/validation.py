import uuid
from functools import wraps
from typing import Iterator
from django.http import HttpResponse, HttpRequest
from backend.api import token
from backend.api.models import Retrospective, RetroStep, IssueAttribute
from .modelsV2 import RetroStepV2
import importlib
from typing import Optional, Union, List


charset_utf8 = 'UTF-8'
content_type_text_plain = 'text/plain'
retro_not_found = 'Retro {} not found'
user_not_admin = 'User is not valid or not an admin'
user_not_valid = 'User is not valid'
issue_not_found = 'Issue {} not found'
user_is_not_issue_owner = 'User is not owner of issue {}'
incorrect_api_version = 'Using incorrect API version.  Utilizing API version {} when retrospective is version {}.'


def retrospective_exists(original_function):
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        retro_id: uuid = kwargs['retro_id']
        retro_id_str: str = str(retro_id)

        request: HttpRequest = args[1]
        service = _get_service(request)

        retro: Retrospective = None
        try:
            retro = service.get_retro(retro_id_str)
        except Retrospective.DoesNotExist:
            return HttpResponse(retro_not_found.format(retro_id_str), status=404, content_type=content_type_text_plain,
                                charset=charset_utf8)

        return original_function(*args, retro=retro, **kwargs)

    return wrapper


def user_is_admin(original_function):
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        request: HttpRequest = args[1]
        retro: Retrospective = kwargs['retro']

        if not token.token_is_admin(token.get_token_from_request(request), retro):
            return HttpResponse(user_not_admin, status=401, content_type=content_type_text_plain, charset=charset_utf8)

        return original_function(*args, **kwargs)

    return wrapper


def user_is_valid(original_function):
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        request: HttpRequest = args[1]
        retro: Retrospective = kwargs['retro']

        if not token.token_is_valid(token.get_token_from_request(request), retro):
            return HttpResponse(user_not_valid, status=401, content_type=content_type_text_plain, charset=charset_utf8)

        return original_function(*args, **kwargs)

    return wrapper


def retro_on_step(retro_step: Union[RetroStep, RetroStepV2, List[RetroStep], List[RetroStepV2]], error_message: str):
    def decorator(original_function):
        @wraps(original_function)
        def wrapper(*args, **kwargs):
            retro: Retrospective = kwargs['retro']

            match = False

            if isinstance(retro_step, list):
                for a_step in retro_step:
                    if retro.current_step == a_step.value:
                        match = True
            else:
                match = retro.current_step == retro_step.value

            if not match:
                return HttpResponse(error_message.format(retro.current_step), status=422,
                                    content_type=content_type_text_plain, charset=charset_utf8)

            return original_function(*args, **kwargs)

        return wrapper
    return decorator


def issue_exists(original_function):
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        issue_id: uuid = kwargs['issue_id']
        issue_id_str: str = str(issue_id)
        retro: Retrospective = kwargs['retro']

        issue: IssueAttribute = _find_issue(issue_id_str, retro)
        if issue is None:
            return HttpResponse(issue_not_found.format(issue_id_str), status=404, content_type=content_type_text_plain,
                                charset=charset_utf8)

        return original_function(*args, issue=issue, **kwargs)

    return wrapper


def issue_owned_by_user(original_function):
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        request: HttpRequest = args[1]
        issue: IssueAttribute = kwargs['issue']

        if not token.issue_owned_by_participant(issue, token.get_token_from_request(request)):
            return HttpResponse(user_is_not_issue_owner.format(issue.id), status=401,
                                content_type=content_type_text_plain, charset=charset_utf8)

        return original_function(*args, **kwargs)

    return wrapper


def retrospective_api_is_correct(original_function):
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        request: HttpRequest = args[1]
        retro: Retrospective = kwargs['retro']

        api_version = _get_api_version(request)
        retro_version = _get_retro_version(retro)

        if api_version != retro_version:
            return HttpResponse(incorrect_api_version.format(api_version, retro_version), status=409,
                                content_type=content_type_text_plain, charset=charset_utf8)

        return original_function(*args, **kwargs)

    return wrapper


def _find_issue(issue_id: str, retro: Retrospective) -> Optional[IssueAttribute]:
    issue_iterator: Iterator[IssueAttribute] = filter(lambda current_issue: current_issue.id == issue_id, retro.issues)
    try:
        return issue_iterator.__next__()
    except StopIteration:
        return None


def _get_api_version(request: HttpRequest) -> str:
    return request.META.get('HTTP_API_VERSION', '1')


def _get_service_version(request: HttpRequest) -> str:
    api_version = _get_api_version(request)

    service_version = 'V' + api_version if api_version != '1' else ''

    return service_version


def _find_service_class_to_use(service_version: str):
    module = importlib.import_module('..service{}'.format(service_version), __name__)
    class_to_use = getattr(module, 'Service{}'.format(service_version))

    return class_to_use


def _get_service(request: HttpRequest):
    service_version = _get_service_version(request)

    return _find_service_class_to_use(service_version)


def _get_retro_version(retro) -> str:
    retro_version = getattr(retro, 'version', '1')
    retro_version = '1' if retro_version is None else retro_version

    return retro_version
