import uuid
from functools import wraps
from typing import Any, Iterator

from django.http import HttpResponse, HttpRequest
from backend.api import service, token
from backend.api.models import Retrospective, RetroStep, IssueAttribute

charset_utf8 = 'UTF-8'
content_type_text_plain = 'text/plain'
retro_not_found = 'Retro {} not found'
user_not_admin = 'User is not valid or not an admin'
user_not_valid = 'User is not valid'
issue_not_found = 'Issue {} not found'
user_is_not_issue_owner = 'User is not owner of issue {}'


def retrospective_exists(original_function):
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        retro_id: uuid = kwargs['retro_id']
        retro_id_str: str = str(retro_id)

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


def retro_on_step(retro_step: RetroStep, error_message: str):
    def decorator(original_function):
        @wraps(original_function)
        def wrapper(*args, **kwargs):
            retro: Retrospective = kwargs['retro']

            if RetroStep(retro.current_step) != retro_step:
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


def _find_issue(issue_id: str, retro: Retrospective) -> IssueAttribute:
    issue_iterator: Iterator[IssueAttribute] = filter(lambda current_issue: current_issue.id == issue_id, retro.issues)
    try:
        return issue_iterator.__next__()
    except StopIteration:
        return None
