from unittest.mock import MagicMock
from backend.api.models import RetroStep


def create_mock_retro(id='retro_id', name='retro_name', current_step=RetroStep.ADDING_ISSUES.value, issues=[],
                      participants=[]):
    retro = MagicMock()

    retro.id = id
    retro.name = name
    retro.current_step = current_step
    retro.issues = issues
    retro.participants = participants

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


def create_mock_participant(name='participant_name', token='creator-token', ready=False, admin=False):
    participant = MagicMock()

    participant.name = name
    participant.token = token
    participant.ready = ready
    participant.admin = admin

    return participant
