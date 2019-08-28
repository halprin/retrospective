import uuid
from typing import Iterator, Optional
from backend.api.models import IssueAttribute, Retrospective, ParticipantAttribute
from .views.generic.utils import Request


def generate_token() -> str:
    return str(uuid.uuid4())


def get_token_from_request(request: Request) -> str:
    return request.headers.get('Authorization', '')[len('Bearer '):]


def issue_owned_by_participant(issue: IssueAttribute, token: str) -> bool:
    return issue.creator_token == token


def get_participant(token: str, retro: Retrospective) -> ParticipantAttribute:
    return _find_participant(lambda participant: get_token_from_model(participant) == token, retro)


def get_participant_via_connection_id(connection_id: str, retro: Retrospective) -> ParticipantAttribute:
    return _find_participant(lambda participant: get_connection_id_from_model(participant) == connection_id, retro)


def token_is_valid(token: str, retro: Retrospective) -> bool:
    return get_participant(token, retro) is not None


def token_is_admin(token: str, retro: Retrospective) -> bool:
    return _find_participant(
        lambda participant: participant.admin is True and get_token_from_model(participant) == token,
        retro) is not None


def add_connection_id(retro, participant, connection_id):
    participant.token = '{}:{}'.format(get_token_from_model(participant), connection_id)
    retro.save()


def _find_participant(func, retro: Retrospective) -> Optional[ParticipantAttribute]:
    participant_iterator: Iterator[ParticipantAttribute] = filter(func, retro.participants)
    try:
        return next(participant_iterator)
    except StopIteration:
        return None


def get_token_from_model(participant: ParticipantAttribute):
    full_token = participant.token
    return full_token[:36]


def get_connection_id_from_model(participant: ParticipantAttribute):
    full_token = participant.token
    return full_token[37:]
