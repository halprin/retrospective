from typing import List
from backend.api.models import Retrospective, ParticipantAttribute, IssueAttribute, RetroStep
import uuid
from backend.api import token
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import pickle


class Service:
    @staticmethod
    def create_retro(retro_name: str, admin_name: str) -> Retrospective:
        new_retro: Retrospective = Retrospective(str(uuid.uuid4()))

        new_retro.name = retro_name
        new_retro.current_step = RetroStep.ADDING_ISSUES.value
        new_retro.participants = [Service._create_participant(admin_name, is_admin=True)]
        new_retro.issues = []

        new_retro.save()

        return new_retro

    @staticmethod
    def get_retro(retro_id: str) -> Retrospective:
        return Retrospective.get(retro_id)

    @staticmethod
    def _reset_ready_statuses(retro: Retrospective):
        for participant in retro.participants:
            participant.ready = False

    @staticmethod
    def move_retro(retro: Retrospective, direction: str) -> str:
        current_step: RetroStep = RetroStep(retro.current_step)

        if direction == 'next':
            retro.current_step = current_step.next().value
        elif direction == 'previous':
            retro.current_step = current_step.previous().value
        else:
            raise ValueError('{} is not a valid direction'.format(direction))

        Service._reset_ready_statuses(retro)

        retro.save()

        Service._send_retro_update(retro)

        return retro.current_step

    @staticmethod
    def _sanitize_participant_list(retro: Retrospective, user_token: str) -> List[dict]:
        is_admin: bool = token.token_is_admin(user_token, retro)

        if is_admin:
            return [{'name': participant.name, 'ready': participant.ready} for participant in retro.participants]
        else:
            return [{'name': participant.name} for participant in retro.participants]

    @staticmethod
    def _get_issue_votes(issue: dict) -> int:
        return issue['votes']

    @staticmethod
    def _sanitize_issue_list(retro: Retrospective, user_token: str) -> List[dict]:
        current_step: RetroStep = RetroStep(retro.current_step)

        sanitized_issues: List[dict] = []

        for issue in retro.issues:
            sanitized_issue: dict = {}
            if issue.creator_token == user_token or current_step != RetroStep.ADDING_ISSUES:
                sanitized_issue['id'] = issue.id
                sanitized_issue['title'] = issue.title
            sanitized_issue['section'] = issue.section
            if current_step == RetroStep.RESULTS:
                sanitized_issue['votes'] = len(issue.votes) if issue.votes is not None else 0
            elif current_step == RetroStep.VOTING:
                sanitized_issue['votes'] = len(
                    [voter for voter in issue.votes if voter == user_token]) if issue.votes is not None else 0
            sanitized_issues.append(sanitized_issue)

        if current_step == RetroStep.RESULTS:
            sanitized_issues.sort(key=Service._get_issue_votes, reverse=True)

        return sanitized_issues

    @staticmethod
    def _construct_yourself_info(retro: Retrospective, user_token: str) -> dict:
        yourself: ParticipantAttribute = token.get_participant(user_token, retro)
        return {
            'name': yourself.name,
            'ready': yourself.ready,
            'admin': yourself.admin
        }

    @staticmethod
    def sanitize_retro_for_user_and_step(retro: Retrospective, user_token: str) -> dict:
        sanitized_retro = {
            'id': retro.id,
            'name': retro.name,
            'currentStep': retro.current_step,
            'participants': Service._sanitize_participant_list(retro, user_token),
            'issues': Service._sanitize_issue_list(retro, user_token),
            'yourself': Service._construct_yourself_info(retro, user_token)
        }

        return sanitized_retro

    @staticmethod
    def _create_participant(name: str, is_admin: bool=False) -> ParticipantAttribute:
        return ParticipantAttribute(name=name, ready=False, admin=is_admin, token=token.generate_token())

    @staticmethod
    def add_participant(name: str, retro: Retrospective) -> str:
        new_participant: ParticipantAttribute = Service._create_participant(name)

        retro.participants.append(new_participant)
        retro.save()

        Service._send_retro_update(retro)

        return new_participant.token

    @staticmethod
    def mark_user_as_ready(user_token: str, is_ready: bool, retro: Retrospective):
        for participant in retro.participants:
            if participant.token == user_token:
                participant.ready = is_ready
                break

        retro.save()

        Service._send_retro_update(retro)

    @staticmethod
    def _create_issue(title: str, section: str, creator_token: str) -> IssueAttribute:
        return IssueAttribute(id=str(uuid.uuid4()), title=title, section=section, creator_token=creator_token, votes=None)

    @staticmethod
    def add_new_issue(title: str, section: str, user_token: str, retro: Retrospective) -> str:
        new_issue: IssueAttribute = Service._create_issue(title, section, creator_token=user_token)

        retro.issues.append(new_issue)
        retro.save()

        Service._send_retro_update(retro)

        return new_issue.id

    @staticmethod
    def vote_for_issue(issue: IssueAttribute, user_token: str, retro: Retrospective):
        if issue.votes is None:
            issue.votes: set = set()
        issue.votes.add(user_token)

        retro.save()

        Service._send_retro_update(retro)

    @staticmethod
    def unvote_for_issue(issue: IssueAttribute, user_token: str, retro: Retrospective):
        if issue.votes is None:
            return
        issue.votes.discard(user_token)

        if len(issue.votes) == 0:
            issue.votes = None

        retro.save()

        Service._send_retro_update(retro)

    @staticmethod
    def delete_issue(issue: IssueAttribute, retro: Retrospective):
        retro.issues.remove(issue)

        retro.save()

        Service._send_retro_update(retro)

    @staticmethod
    def _send_retro_update(retro: Retrospective):
        async_to_sync(get_channel_layer().group_send)(retro.id, {
            'type': 'disburse.update',
            'retro': pickle.dumps(retro)
        })
