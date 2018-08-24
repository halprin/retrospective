import uuid
from backend.api.modelsV2 import RetrospectiveV2, RetroStepV2, IssueAttributeV2, GroupAttribute
from backend.api.service import Service


class ServiceV2(Service):
    @classmethod
    def create_retro(cls, retro_name: str, admin_name: str) -> RetrospectiveV2:
        new_retro: RetrospectiveV2 = RetrospectiveV2(str(uuid.uuid4()))

        new_retro.name = retro_name
        new_retro.current_step = RetroStepV2.ADDING_ISSUES.value
        new_retro.participants = [cls._create_participant(admin_name, is_admin=True)]
        new_retro.issues = []
        new_retro.groups = []
        new_retro.version = '2'

        new_retro.save()

        return new_retro

    @staticmethod
    def get_retro(retro_id: str) -> RetrospectiveV2:
        return RetrospectiveV2.get(retro_id)

    @staticmethod
    def _get_retro_step(step: str) -> RetroStepV2:
        return RetroStepV2(step)

    @staticmethod
    def _is_adding_issues_step(step: RetroStepV2) -> bool:
        return step is RetroStepV2.ADDING_ISSUES

    @staticmethod
    def _is_grouping_step(step: RetroStepV2) -> bool:
        return step is RetroStepV2.GROUPING

    @staticmethod
    def _is_voting_step(step: RetroStepV2) -> bool:
        return step is RetroStepV2.VOTING

    @staticmethod
    def _is_results_step(step: RetroStepV2) -> bool:
        return step == RetroStepV2.RESULTS

    @classmethod
    def _sanitize_issue(cls, issue: IssueAttributeV2, current_step: RetroStepV2, user_token: str) -> dict:
        sanitized_issue: dict = super(ServiceV2, cls)._sanitize_issue(issue, current_step, user_token)

        sanitized_issue['group'] = issue.group

        return sanitized_issue

    @classmethod
    def _sanitize_group(cls, group: GroupAttribute, current_step: RetroStepV2, user_token: str):
        sanitized_group: dict = {'id': group.id, 'title': group.title, 'section': group.section}

        if cls._is_results_step(current_step):
            sanitized_group['votes'] = len(group.votes) if group.votes is not None else 0
        elif cls._is_voting_step(current_step):
            sanitized_group['votes'] = len(
                [voter for voter in group.votes if voter == user_token]) if group.votes is not None else 0

        return sanitized_group

    @classmethod
    def _sanitize_group_list(cls, retro: RetrospectiveV2, user_token: str):
        retro_step: RetroStepV2 = cls._get_retro_step(retro.current_step)
        return [cls._sanitize_group(group, retro_step, user_token) for group in retro.groups]

    @classmethod
    def sanitize_retro_for_user_and_step(cls, retro: RetrospectiveV2, user_token: str) -> dict:
        sanitized_retro = {
            'id': retro.id,
            'name': retro.name,
            'currentStep': retro.current_step,
            'participants': cls._sanitize_participant_list(retro, user_token),
            'issues': cls._sanitize_issue_list(retro, user_token),
            'groups': cls._sanitize_group_list(retro, user_token),
            'yourself': cls._construct_yourself_info(retro, user_token)
        }

        return sanitized_retro

    @staticmethod
    def _create_issue(title: str, section: str, creator_token: str) -> IssueAttributeV2:
        return IssueAttributeV2(id=str(uuid.uuid4()), title=title, section=section, creator_token=creator_token,
                                votes=None, group='')

    @staticmethod
    def _get_group_by_id(group_id: str, retro: RetrospectiveV2) -> GroupAttribute:

        group_finder = (group for group in retro.groups if group.id == group_id)

        try:
            return next(group_finder)
        except StopIteration:
            return None

    @classmethod
    def vote_for_issue(cls, issue: IssueAttributeV2, user_token: str, retro: RetrospectiveV2):
        if issue.group is not None and issue.group != '':
            group: GroupAttribute = cls._get_group_by_id(issue.group, retro)
            cls.vote_for_group(group, user_token, retro)
            return

        super(ServiceV2, cls).vote_for_issue(issue, user_token, retro)

    @classmethod
    def vote_for_group(cls, group: GroupAttribute, user_token: str, retro: RetrospectiveV2):
        if group.votes is None:
            group.votes: set = set()
        group.votes.add(user_token)

        retro.save()

        cls._send_retro_update(retro)

    @classmethod
    def unvote_for_issue(cls, issue: IssueAttributeV2, user_token: str, retro: RetrospectiveV2):
        if issue.group is not None and issue.group != '':
            group: GroupAttribute = cls._get_group_by_id(issue.group, retro)
            cls.unvote_for_group(group, user_token, retro)
            return

        super(ServiceV2, cls).unvote_for_issue(issue, user_token, retro)

    @classmethod
    def unvote_for_group(cls, group: GroupAttribute, user_token: str, retro: RetrospectiveV2):
        if group.votes is None:
            return
        group.votes.discard(user_token)

        if len(group.votes) == 0:
            group.votes = None

        retro.save()

        cls._send_retro_update(retro)

    @classmethod
    def group_issue(cls, issue: IssueAttributeV2, group: GroupAttribute, retro: RetrospectiveV2):
        issue.group = group.id

        retro.save()

        cls._send_retro_update(retro)

    @classmethod
    def ungroup_issue(cls, issue: IssueAttributeV2, retro: RetrospectiveV2):
        issue.group = None

        retro.save()

        cls._send_retro_update(retro)
