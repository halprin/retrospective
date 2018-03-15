from backend.api.models import Retrospective, ParticipantAttribute, IssueAttribute, RetroStep
import uuid
from backend.api import token


def create_retro(retro_name, admin_name):
    new_retro = Retrospective(str(uuid.uuid4()))

    new_retro.name = retro_name
    new_retro.current_step = RetroStep.ADDING_ISSUES.value
    new_retro.participants = [_create_participant(admin_name, is_admin=True)]
    new_retro.issues = []

    new_retro.save()

    return new_retro


def get_retro(retro_id):
    return Retrospective.get(retro_id)


def _reset_ready_statuses(retro):
    for participant in retro.participants:
        participant.ready = False


def move_retro(retro, direction):
    current_step = RetroStep(retro.current_step)

    if direction == 'next':
        retro.current_step = current_step.next().value
    elif direction == 'previous':
        retro.current_step = current_step.previous().value
    else:
        raise ValueError('{} is not a valid direction'.format(direction))

    _reset_ready_statuses(retro)

    retro.save()

    return retro.current_step


def _sanitize_participant_list(retro, user_token):
    is_admin = token.token_is_admin(user_token, retro)

    if is_admin:
        return [{'name': participant.name, 'ready': participant.ready} for participant in retro.participants]
    else:
        return [{'name': participant.name} for participant in retro.participants]


def _sanitize_issue_list(retro, user_token):
    current_step = RetroStep(retro.current_step)

    sanitized_issues = []

    for issue in retro.issues:
        sanitized_issue = {}
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

    return sanitized_issues


def _construct_yourself_info(retro, user_token):
    yourself = token.get_participant(user_token, retro)
    return {
        'name': yourself.name,
        'ready': yourself.ready,
        'admin': yourself.admin
    }


def sanitize_retro_for_user_and_step(retro, user_token):
    sanitized_retro = {
        'id': retro.id,
        'name': retro.name,
        'currentStep': retro.current_step,
        'participants': _sanitize_participant_list(retro, user_token),
        'issues': _sanitize_issue_list(retro, user_token),
        'yourself': _construct_yourself_info(retro, user_token)
    }

    return sanitized_retro


def _create_participant(name, is_admin=False):
    return ParticipantAttribute(name=name, ready=False, admin=is_admin, token=token.generate_token())


def add_participant(name, retro):
    new_participant = _create_participant(name)

    retro.participants.append(new_participant)
    retro.save()

    return new_participant.token


def mark_user_as_ready(user_token, is_ready, retro):
    for participant in retro.participants:
        if participant.token == user_token:
            participant.ready = is_ready
            break

    retro.save()


def _create_issue(title, section, creator_token):
    return IssueAttribute(id=str(uuid.uuid4()), title=title, section=section, creator_token=creator_token, votes=None)


def add_new_issue(title, section, user_token, retro):
    new_issue = _create_issue(title, section, creator_token=user_token)

    retro.issues.append(new_issue)
    retro.save()

    return new_issue.id


def vote_for_issue(issue_id_str, user_token, retro):
    for issue in retro.issues:
        if issue.id == issue_id_str:
            if issue.votes is None:
                issue.votes = set()
            issue.votes.add(user_token)
            break

    retro.save()
