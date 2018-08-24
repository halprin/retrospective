import uuid
from typing import Iterator, Optional
from django.http import HttpRequest
from backend.api.models import IssueAttribute, Retrospective, ParticipantAttribute


def generate_token() -> str:
    return str(uuid.uuid4())


def get_token_from_request(request: HttpRequest) -> str:
    return request.META.get('HTTP_AUTHORIZATION', '')[len('Bearer '):]


def issue_owned_by_participant(issue: IssueAttribute, token: str) -> bool:
    return issue.creator_token == token


def get_participant(token: str, retro: Retrospective) -> ParticipantAttribute:
    return _find_participant(lambda participant: participant.token == token, retro)


def token_is_valid(token: str, retro: Retrospective) -> bool:
    return get_participant(token, retro) is not None


def token_is_admin(token: str, retro: Retrospective) -> bool:
    return _find_participant(lambda participant: participant.admin is True and participant.token == token,
                             retro) is not None


def _find_participant(func, retro: Retrospective) -> Optional[ParticipantAttribute]:
    participant_iterator: Iterator[ParticipantAttribute] = filter(func, retro.participants)
    try:
        return next(participant_iterator)
    except StopIteration:
        return None
