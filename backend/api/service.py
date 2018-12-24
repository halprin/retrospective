from typing import List
from backend.api.models import Retrospective, ParticipantAttribute, IssueAttribute, RetroStep
import uuid
from backend.api import token


class Service:
    @classmethod
    def create_retro(cls, retro_name: str, admin_name: str) -> Retrospective:
        new_retro: Retrospective = Retrospective(str(uuid.uuid4()))

        new_retro.name = retro_name
        new_retro.current_step = RetroStep.ADDING_ISSUES.value
        new_retro.participants = [cls._create_participant(admin_name, is_admin=True)]
        new_retro.issues = []
        new_retro.version = '1'

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
    def _get_retro_step(step: str) -> RetroStep:
        return RetroStep(step)

    @classmethod
    def move_retro(cls, retro: Retrospective, direction: str) -> str:
        current_step = cls._get_retro_step(retro.current_step)

        if direction == 'next':
            retro.current_step = current_step.next().value
        elif direction == 'previous':
            retro.current_step = current_step.previous().value
        else:
            raise ValueError('{} is not a valid direction'.format(direction))

        cls._reset_ready_statuses(retro)

        retro.save()

        cls._send_retro_update(retro)

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

    @classmethod
    def _sanitize_issue(cls, issue: IssueAttribute, current_step: RetroStep, user_token: str) -> dict:
        sanitized_issue: dict = {}

        if issue.creator_token == user_token or not cls._is_adding_issues_step(current_step):
            sanitized_issue['id'] = issue.id
            sanitized_issue['title'] = issue.title
        sanitized_issue['section'] = issue.section
        if cls._is_results_step(current_step):
            sanitized_issue['votes'] = len(issue.votes) if issue.votes is not None else 0
        elif cls._is_voting_step(current_step):
            sanitized_issue['votes'] = len(
                [voter for voter in issue.votes if voter == user_token]) if issue.votes is not None else 0

        return sanitized_issue

    @staticmethod
    def _is_adding_issues_step(current_step: RetroStep) -> bool:
        return current_step is RetroStep.ADDING_ISSUES

    @staticmethod
    def _is_voting_step(current_step: RetroStep) -> bool:
        return current_step is RetroStep.VOTING

    @staticmethod
    def _is_results_step(current_step: RetroStep) -> bool:
        return current_step is RetroStep.RESULTS

    @classmethod
    def _sanitize_issue_list(cls, retro: Retrospective, user_token: str) -> List[dict]:
        current_step = cls._get_retro_step(retro.current_step)

        sanitized_issues: List[dict] = []

        for issue in retro.issues:
            sanitized_issues.append(cls._sanitize_issue(issue, current_step, user_token))

        if cls._is_results_step(current_step):
            sanitized_issues.sort(key=cls._get_issue_votes, reverse=True)

        return sanitized_issues

    @staticmethod
    def _construct_yourself_info(retro: Retrospective, user_token: str) -> dict:
        yourself: ParticipantAttribute = token.get_participant(user_token, retro)
        return {
            'name': yourself.name,
            'ready': yourself.ready,
            'admin': yourself.admin
        }

    @classmethod
    def sanitize_retro_for_user_and_step(cls, retro: Retrospective, user_token: str) -> dict:
        sanitized_retro = {
            'id': retro.id,
            'name': retro.name,
            'currentStep': retro.current_step,
            'participants': cls._sanitize_participant_list(retro, user_token),
            'issues': cls._sanitize_issue_list(retro, user_token),
            'yourself': cls._construct_yourself_info(retro, user_token)
        }

        return sanitized_retro

    @staticmethod
    def _create_participant(name: str, is_admin: bool=False) -> ParticipantAttribute:
        return ParticipantAttribute(name=name, ready=False, admin=is_admin, token=token.generate_token())

    @classmethod
    def add_participant(cls, name: str, retro: Retrospective) -> str:
        new_participant: ParticipantAttribute = cls._create_participant(name)

        retro.participants.append(new_participant)
        retro.save()

        cls._send_retro_update(retro)

        return new_participant.token

    @classmethod
    def mark_user_as_ready(cls, user_token: str, is_ready: bool, retro: Retrospective):
        for participant in retro.participants:
            if participant.token == user_token:
                participant.ready = is_ready
                break

        retro.save()

        cls._send_retro_update(retro)

    @staticmethod
    def _create_issue(title: str, section: str, creator_token: str) -> IssueAttribute:
        return IssueAttribute(id=str(uuid.uuid4()), title=title, section=section, creator_token=creator_token,
                              votes=None)

    @classmethod
    def add_new_issue(cls, title: str, section: str, user_token: str, retro: Retrospective) -> str:
        new_issue = cls._create_issue(title, section, creator_token=user_token)

        retro.issues.append(new_issue)
        retro.save()

        cls._send_retro_update(retro)

        return new_issue.id

    @classmethod
    def vote_for_issue(cls, issue: IssueAttribute, user_token: str, retro: Retrospective):
        if issue.votes is None:
            issue.votes: set = set()
        issue.votes.add(user_token)

        retro.save()

        cls._send_retro_update(retro)

    @classmethod
    def unvote_for_issue(cls, issue: IssueAttribute, user_token: str, retro: Retrospective):
        if issue.votes is None:
            return
        issue.votes.discard(user_token)

        if len(issue.votes) == 0:
            issue.votes = None

        retro.save()

        cls._send_retro_update(retro)

    @classmethod
    def delete_issue(cls, issue: IssueAttribute, retro: Retrospective):
        retro.issues.remove(issue)

        retro.save()

        cls._send_retro_update(retro)

    @staticmethod
    def _send_retro_update(retro: Retrospective):
        # TODO: updated to support the new way to send WebSocket updates to all the subscribers
        pass
