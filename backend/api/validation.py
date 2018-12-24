import uuid
from functools import wraps
from typing import Iterator
from backend.api import token
from backend.api.models import Retrospective, RetroStep, IssueAttribute
from .modelsV2 import RetroStepV2, RetrospectiveV2, GroupAttribute
import importlib
from typing import Optional, Union, List
from pynamodb.models import Model
from .views.generic.utils import Request, Response


charset_utf8 = 'UTF-8'
content_type_text_plain = 'text/plain'
retro_not_found = 'Retro {} not found'
user_not_admin = 'User is not valid or not an admin'
user_not_valid = 'User is not valid'
issue_not_found = 'Issue {} not found'
group_not_found = 'Group {} not found'
user_is_not_issue_owner = 'User is not owner of issue {}'
incorrect_api_version = 'Using incorrect API version.  Utilizing API version {} when retrospective is version {}.'


def retrospective_exists(original_function):
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        request: Request = next(arg for arg in args if isinstance(arg, Request))
        retro_id_str = request.path_values['retro_id']
        service = _get_service(request)

        retro: Retrospective = None
        try:
            retro = service.get_retro(retro_id_str)
        except Model.DoesNotExist:
            return Response(404, retro_not_found.format(retro_id_str), {'Content-Type': content_type_text_plain})

        return original_function(*args, retro=retro, **kwargs)

    return wrapper


def user_is_admin(original_function):
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        request: Request = args[1]
        retro: Retrospective = kwargs['retro']

        if not token.token_is_admin(token.get_token_from_request(request), retro):
            return Response(401, user_not_admin, {'Content-Type': content_type_text_plain})

        return original_function(*args, **kwargs)

    return wrapper


def user_is_valid(original_function):
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        request: Request = next(arg for arg in args if isinstance(arg, Request))
        retro: Retrospective = kwargs['retro']

        if not token.token_is_valid(token.get_token_from_request(request), retro):
            return Response(401, user_not_valid, {'Content-Type': content_type_text_plain})

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
                return Response(422, error_message.format(retro.current_step),
                                {'Content-Type': content_type_text_plain})

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
        request: Request = next(arg for arg in args if isinstance(arg, Request))
        retro: Retrospective = kwargs['retro']

        api_version = _get_api_version(request)
        retro_version = _get_retro_version(retro)

        if api_version != retro_version:
            return Response(409, incorrect_api_version.format(api_version, retro_version),
                            {'Content-Type': content_type_text_plain})

        return original_function(*args, **kwargs)

    return wrapper


def group_exists(original_function):
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        group_id: uuid = kwargs['group_id']
        group_id_str: str = str(group_id)
        retro: RetrospectiveV2 = kwargs['retro']

        group: GroupAttribute = None

        if not isinstance(group_id, bool):
            group = _find_group(group_id_str, retro)
            if group is None:
                return HttpResponse(group_not_found.format(group_id_str), status=404,
                                    content_type=content_type_text_plain, charset=charset_utf8)

        return original_function(*args, group=group, **kwargs)

    return wrapper


def _find_group(group_id: str, retro: RetrospectiveV2) -> Optional[GroupAttribute]:
    group_iterator: Iterator[GroupAttribute] = filter(lambda current_group: current_group.id == group_id, retro.groups)
    try:
        return next(group_iterator)
    except StopIteration:
        return None


def _find_issue(issue_id: str, retro: Retrospective) -> Optional[IssueAttribute]:
    issue_iterator: Iterator[IssueAttribute] = filter(lambda current_issue: current_issue.id == issue_id, retro.issues)
    try:
        return next(issue_iterator)
    except StopIteration:
        return None


def _get_api_version(request: Request) -> str:
    return request.headers.get('Api-Version', '1')


def _get_service_version(request: Request) -> str:
    api_version = _get_api_version(request)

    service_version = 'V' + api_version if api_version != '1' else ''

    return service_version


def _find_service_class_to_use(service_version: str):
    module = importlib.import_module('..service{}'.format(service_version), __name__)
    class_to_use = getattr(module, 'Service{}'.format(service_version))

    return class_to_use


def _get_service(request: Request):
    service_version = _get_service_version(request)

    return _find_service_class_to_use(service_version)


def _get_retro_version(retro) -> str:
    retro_version = getattr(retro, 'version', '1')
    retro_version = '1' if retro_version is None else retro_version

    return retro_version
