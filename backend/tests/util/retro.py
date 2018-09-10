from unittest.mock import MagicMock
from backend.api.models import RetroStep
from backend.api.modelsV2 import RetroStepV2


def create_mock_retro(id='retro_id', name='retro_name', current_step=RetroStep.ADDING_ISSUES.value, issues=[],
                      participants=[]):
    retro = MagicMock()

    retro.id = id
    retro.name = name
    retro.current_step = current_step
    retro.issues = issues
    retro.participants = participants
    retro.version = None

    return retro


def create_mock_retroV2(id='retro_id', name='retro_name', current_step=RetroStepV2.ADDING_ISSUES.value, issues=[],
                        participants=[], groups=[]):
    retro = create_mock_retro(id=id, name=name, current_step=current_step, issues=issues, participants=participants)

    retro.groups = groups
    retro.version = '2'

    return retro


def create_mock_issue(id='issue_id', title='issue_name', section='Start doing', creator_token='creator-token',
                      votes=None):
    issue = MagicMock()

    issue.id = id
    issue.title = title
    issue.section = section
    issue.creator_token = creator_token
    issue.votes = votes

    return issue


def create_mock_issueV2(id='issue_id', title='issue_name', section='Start doing', creator_token='creator-token',
                        votes=None, group=''):
    issue = create_mock_issue(id=id, title=title, section=section, creator_token=creator_token, votes=votes)

    issue.group = group

    return issue


def create_mock_participant(name='participant_name', token='creator-token', ready=False, admin=False):
    participant = MagicMock()

    participant.name = name
    participant.token = token
    participant.ready = ready
    participant.admin = admin

    return participant


def create_mock_group(id='group_id', title='group_name', section='Start doing', votes=None):
    group = MagicMock()

    group.id = id
    group.title = title
    group.section = section
    group.votes = votes

    return group
