from typing import List
from backend.api.models import Retrospective, ParticipantAttribute, IssueAttribute, RetroStep
import uuid
from backend.api import token
import boto3
import json
import os
import logging


class Service:
    @classmethod
    def create_retro(cls, retro_name: str, admin_name: str) -> Retrospective:
        new_retro: Retrospective = Retrospective(str(uuid.uuid4()))
        logging.info('Creating retrospective {}'.format(new_retro.id))

        new_retro.name = retro_name
        new_retro.current_step = RetroStep.ADDING_ISSUES.value
        new_retro.participants = [cls._create_participant(admin_name, is_admin=True)]
        new_retro.issues = []
        new_retro.version = '1'

        new_retro.save()

        return new_retro

    @staticmethod
    def get_retro(retro_id: str) -> Retrospective:
        logging.info('Getting retrospective {}'.format(retro_id))
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
        logging.info('Moving retrospective {}, {}'.format(retro.id, direction))
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
        logging.info('Sanitizing retrospective {} for user {}'.format(retro.id, user_token))
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
    def _create_participant(name: str, is_admin: bool = False) -> ParticipantAttribute:
        return ParticipantAttribute(name=name, ready=False, admin=is_admin, token=token.generate_token())

    @classmethod
    def add_participant(cls, name: str, retro: Retrospective) -> str:
        logging.info('Adding new participant {} to retrospective {}'.format(name, retro.id))
        new_participant: ParticipantAttribute = cls._create_participant(name)

        retro.participants.append(new_participant)
        retro.save()

        cls._send_retro_update(retro)

        return new_participant.token

    @classmethod
    def mark_user_as_ready(cls, user_token: str, is_ready: bool, retro: Retrospective):
        logging.info('Marking participant {} as ready'.format(user_token))
        participant = token.get_participant(user_token, retro)
        participant.ready = is_ready

        retro.save()

        cls._send_retro_update(retro)

    @staticmethod
    def _create_issue(title: str, section: str, creator_token: str) -> IssueAttribute:
        return IssueAttribute(id=str(uuid.uuid4()), title=title, section=section, creator_token=creator_token,
                              votes=None)

    @classmethod
    def add_new_issue(cls, title: str, section: str, user_token: str, retro: Retrospective) -> str:
        logging.info(
            'Adding new issue "{}" into section "{}" by user {} on retrospective {}'.format(title, section, user_token,
                                                                                            retro.id))
        new_issue = cls._create_issue(title, section, creator_token=user_token)

        retro.issues.append(new_issue)
        retro.save()

        cls._send_retro_update(retro)

        return new_issue.id

    @classmethod
    def vote_for_issue(cls, issue: IssueAttribute, user_token: str, retro: Retrospective):
        logging.info('Participant {} voting for issue {} on retrospective {}'.format(user_token, issue.id, retro.id))
        if issue.votes is None:
            issue.votes: set = set()
        issue.votes.add(user_token)

        retro.save()

        cls._send_retro_update(retro)

    @classmethod
    def unvote_for_issue(cls, issue: IssueAttribute, user_token: str, retro: Retrospective):
        logging.info('Participant {} unvoting for issue {} on retrospective {}'.format(user_token, issue.id, retro.id))
        if issue.votes is None:
            return
        issue.votes.discard(user_token)

        if len(issue.votes) == 0:
            issue.votes = None

        retro.save()

        cls._send_retro_update(retro)

    @classmethod
    def delete_issue(cls, issue: IssueAttribute, retro: Retrospective):
        logging.info('Deleting issue {} on retrospective {}'.format(issue.id, retro.id))
        retro.issues.remove(issue)

        retro.save()

        cls._send_retro_update(retro)

    @classmethod
    def _send_retro_update(cls, retro: Retrospective):
        websocket_endpoint = os.environ['WEBSOCKET_ENDPOINT']
        client = boto3.Session().client('apigatewaymanagementapi',
                                        endpoint_url=websocket_endpoint)
        for participant in retro.participants:
            cls._send_retro_update_to_participant(retro, participant, client)

    @classmethod
    def _send_retro_update_to_participant(cls, retro: Retrospective, participant: ParticipantAttribute,
                                          apigatewaymanagementapi_client):
        connection_id = token.get_connection_id_from_model(participant)
        if connection_id == '':
            return
        user_token = token.get_token_from_model(participant)
        sanitized_retro = cls.sanitize_retro_for_user_and_step(retro, user_token)
        sanitized_retro_json = json.dumps(sanitized_retro)
        try:
            apigatewaymanagementapi_client.post_to_connection(Data=sanitized_retro_json.encode('utf-8'),
                                                              ConnectionId=connection_id)
        except Exception:
            logging.warning('Participant {} WebSocket is no longer connected; removing connection ID'.format(participant.name))
            participant.token = user_token
            retro.save()
