from backend.api import service
import pytest
from backend.tests.util import retro
import copy
from backend.api.models import RetroStep
from unittest.mock import patch, MagicMock, PropertyMock


@patch('backend.api.service.Retrospective', autospec=True)
def test_create_retro(mock_retrospective_class):
    retro_name = 'Sprint 26'
    admin_name = 'DogCow'
    mock_retrospective_class.side_effect = lambda retro_id: retro.create_mock_retro(id=retro_id)

    new_retro = service.create_retro(retro_name, admin_name)

    assert new_retro.name == retro_name
    assert new_retro.current_step == RetroStep.ADDING_ISSUES.value
    assert len(new_retro.participants) == 1
    assert new_retro.participants[0].name == admin_name
    assert new_retro.participants[0].admin is True
    assert len(new_retro.issues) == 0
    assert new_retro.id is not None


@patch('backend.api.service.Retrospective', autospec=True)
def test_get_retro(mock_retrospective_class):
    retro_id = 'an_awesome_retro_id'
    mock_retrospective_class.get.side_effect = lambda passed_in_retro_id: retro.create_mock_retro(id=passed_in_retro_id)

    returned_retro = service.get_retro(retro_id)

    mock_retrospective_class.get.assert_called_with(retro_id)
    assert returned_retro.id == retro_id


def test__reset_ready_statuses():
    participant1 = retro.create_mock_participant(ready=True)
    participant2 = retro.create_mock_participant(ready=False)
    participant3 = retro.create_mock_participant(ready=True)
    a_retro = retro.create_mock_retro(participants=[participant1, participant2, participant3])

    service._reset_ready_statuses(a_retro)

    for participant in a_retro.participants:
        assert participant.ready is False


def test_move_retro_unknown_direction():
    step = RetroStep.VOTING
    a_retro = retro.create_mock_retro(current_step=step.value)

    with pytest.raises(ValueError):
        service.move_retro(a_retro, 'lollerskates')

    assert a_retro.current_step == step.value


@patch('backend.api.service._send_retro_update', autospec=True)
def test_move_retro_previous(mock_send_retro_update):
    step = RetroStep.RESULTS
    a_retro = retro.create_mock_retro(current_step=step.value)

    new_step = service.move_retro(a_retro, 'previous')

    assert new_step == step.previous().value
    assert a_retro.current_step == step.previous().value
    a_retro.save.assert_called_with()
    mock_send_retro_update.assert_called_once()


@patch('backend.api.service._send_retro_update', autospec=True)
def test_move_retro_next(mock_send_retro_update):
    step = RetroStep.ADDING_ISSUES
    a_retro = retro.create_mock_retro(current_step=step.value)

    new_step = service.move_retro(a_retro, 'next')

    assert new_step == step.next().value
    assert a_retro.current_step == step.next().value
    a_retro.save.assert_called_with()
    mock_send_retro_update.assert_called_once()


def test__sanitize_participant_list_when_not_admin():
    your_token = 'a-token'
    your_participant = retro.create_mock_participant('your_name', token=your_token, ready=False, admin=False)
    another_participant = retro.create_mock_participant('another_name', token='another-token', ready=True, admin=False)
    a_retro = retro.create_mock_retro(current_step=RetroStep.ADDING_ISSUES,
                                      participants=[your_participant, another_participant])

    sanitized_participants = service._sanitize_participant_list(a_retro, your_token)

    assert len(sanitized_participants) == 2
    assert sanitized_participants[0]['name'] == your_participant.name
    with pytest.raises(KeyError):
        sanitized_participants[0]['ready']
    assert sanitized_participants[1]['name'] == another_participant.name
    with pytest.raises(KeyError):
        sanitized_participants[1]['ready']


def test__sanitize_participant_list_when_admin():
    your_token = 'a-token'
    your_participant = retro.create_mock_participant('your_name', token=your_token, ready=False, admin=True)
    another_participant = retro.create_mock_participant('another_name', token='another-token', ready=True, admin=False)
    a_retro = retro.create_mock_retro(current_step=RetroStep.ADDING_ISSUES,
                                      participants=[your_participant, another_participant])

    sanitized_participants = service._sanitize_participant_list(a_retro, your_token)

    assert len(sanitized_participants) == 2
    assert sanitized_participants[0]['name'] == your_participant.name
    assert sanitized_participants[0]['ready'] == your_participant.ready
    assert sanitized_participants[1]['name'] == another_participant.name
    assert sanitized_participants[1]['ready'] == another_participant.ready


def test__sanitize_issue_list_shows_all_votes_during_results():
    your_token = 'a-token'
    your_issue = retro.create_mock_issue(section='your_section', creator_token=your_token,
                                         votes={'another-different-token'})
    another_issue = retro.create_mock_issue(section='special_section', creator_token='a-different-token',
                                            votes={your_token, 'another-different-token'})
    yet_another_issue = retro.create_mock_issue(section='special_section', creator_token='a-different-token')
    a_retro = retro.create_mock_retro(current_step=RetroStep.RESULTS,
                                      issues=[your_issue, another_issue, yet_another_issue])

    sanitized_issues = service._sanitize_issue_list(a_retro, your_token)

    assert len(sanitized_issues) == 3
    was_another_issue = sanitized_issues[0]
    assert was_another_issue['id'] == another_issue.id
    assert was_another_issue['title'] == another_issue.title
    assert was_another_issue['section'] == another_issue.section
    assert was_another_issue['votes'] == 2
    was_your_issue = sanitized_issues[1]
    assert was_your_issue['id'] == your_issue.id
    assert was_your_issue['title'] == your_issue.title
    assert was_your_issue['section'] == your_issue.section
    assert was_your_issue['votes'] == 1
    was_yet_another_issue = sanitized_issues[2]
    assert was_yet_another_issue['votes'] == 0


def test___get_issue_votes():
    value = 'moof'
    input_dictionary = {'votes': value}

    output = service._get_issue_votes(input_dictionary)

    assert output == value


def test__sanitize_issue_list_orders_issues_by_vote_count():
    your_token = 'a-token'
    the_issue_section = 'a-section'
    another_issue_section = 'another-section'

    first_issue = retro.create_mock_issue(id='1', section=the_issue_section, creator_token=your_token,
                                          votes=set())
    second_issue = retro.create_mock_issue(id='3', section=the_issue_section, creator_token='a-different-token',
                                          votes={your_token, 'another-different-token', 'yet-another-token'})
    third_issue = retro.create_mock_issue(id='2', section=another_issue_section, creator_token='a-different-token',
                                           votes={your_token})

    a_retro = retro.create_mock_retro(current_step=RetroStep.RESULTS,
                                      issues=[first_issue, second_issue, third_issue])

    sanitized_issues = service._sanitize_issue_list(a_retro, your_token)

    assert sanitized_issues[0]['id'] == second_issue.id
    assert sanitized_issues[1]['id'] == third_issue.id
    assert sanitized_issues[2]['id'] == first_issue.id


def test__sanitize_issue_list_doesnt_order_issues_when_not_results():
    your_token = 'a-token'
    the_issue_section = 'a-section'
    another_issue_section = 'another-section'

    first_issue = retro.create_mock_issue(id='1', section=the_issue_section, creator_token=your_token,
                                          votes=set())
    second_issue = retro.create_mock_issue(id='3', section=the_issue_section, creator_token='a-different-token',
                                           votes={your_token, 'another-different-token', 'yet-another-token'})
    third_issue = retro.create_mock_issue(id='2', section=another_issue_section, creator_token='a-different-token',
                                          votes={your_token})

    a_retro = retro.create_mock_retro(current_step=RetroStep.VOTING,
                                      issues=[first_issue, second_issue, third_issue])

    sanitized_issues = service._sanitize_issue_list(a_retro, your_token)

    assert sanitized_issues[0]['id'] == first_issue.id
    assert sanitized_issues[1]['id'] == second_issue.id
    assert sanitized_issues[2]['id'] == third_issue.id


def test__sanitize_issue_list_shows_your_votes_during_voting():
    your_token = 'a-token'
    your_issue = retro.create_mock_issue(section='your_section', creator_token=your_token,
                                         votes={'another-different-token'})
    another_issue = retro.create_mock_issue(section='special_section', creator_token='a-different-token',
                                            votes={your_token, 'another-different-token'})
    a_retro = retro.create_mock_retro(current_step=RetroStep.VOTING, issues=[your_issue, another_issue])

    sanitized_issues = service._sanitize_issue_list(a_retro, your_token)

    assert len(sanitized_issues) == 2
    was_your_issue = sanitized_issues[0]
    assert was_your_issue['id'] == your_issue.id
    assert was_your_issue['title'] == your_issue.title
    assert was_your_issue['section'] == your_issue.section
    assert was_your_issue['votes'] == 0
    was_another_issue = sanitized_issues[1]
    assert was_another_issue['id'] == another_issue.id
    assert was_another_issue['title'] == another_issue.title
    assert was_another_issue['section'] == another_issue.section
    assert was_another_issue['votes'] == 1


def test__sanitize_issue_list_shows_all_issues_no_votes_yet_during_voting():
    user_token = 'a-token'
    your_issue = retro.create_mock_issue(section='your_section', creator_token=user_token)
    another_issue = retro.create_mock_issue(section='special_section', creator_token='a-different-token')
    a_retro = retro.create_mock_retro(current_step=RetroStep.VOTING, issues=[your_issue, another_issue])

    sanitized_issues = service._sanitize_issue_list(a_retro, user_token)

    assert len(sanitized_issues) == 2
    was_your_issue = sanitized_issues[0]
    assert was_your_issue['id'] == your_issue.id
    assert was_your_issue['title'] == your_issue.title
    assert was_your_issue['section'] == your_issue.section
    assert was_your_issue['votes'] == 0
    was_another_issue = sanitized_issues[1]
    assert was_another_issue['id'] == another_issue.id
    assert was_another_issue['title'] == another_issue.title
    assert was_another_issue['section'] == another_issue.section
    assert was_another_issue['votes'] == 0


def test__sanitize_issue_list_shows_my_issues_and_other_sections_during_adding_issues():
    user_token = 'a-token'
    your_issue = retro.create_mock_issue(section='your_section', creator_token=user_token, votes={user_token})
    another_issue = retro.create_mock_issue(section='special_section', creator_token='a-different-token')
    a_retro = retro.create_mock_retro(current_step=RetroStep.ADDING_ISSUES, issues=[your_issue, another_issue])

    sanitized_issues = service._sanitize_issue_list(a_retro, user_token)

    assert len(sanitized_issues) == 2
    was_your_issue = sanitized_issues[0]
    assert was_your_issue['id'] == your_issue.id
    assert was_your_issue['title'] == your_issue.title
    assert was_your_issue['section'] == your_issue.section
    with pytest.raises(KeyError):
        was_your_issue['votes']
    was_another_issue = sanitized_issues[1]
    assert was_another_issue['section'] == another_issue.section
    with pytest.raises(KeyError):
        was_another_issue['title']
    with pytest.raises(KeyError):
        was_another_issue['id']
    with pytest.raises(KeyError):
        was_another_issue['votes']


def test__construct_yourself_info():
    test_token = 'asdf-jkl'
    test_name = 'Johny'
    test_ready = True
    test_admin = True
    participant1 = retro.create_mock_participant(token='junk')
    participant2 = retro.create_mock_participant(name=test_name, token=test_token, ready=test_ready, admin=test_admin)
    a_retro = retro.create_mock_retro(participants=[participant1, participant2])

    yourself = service._construct_yourself_info(a_retro, test_token)

    assert yourself['name'] == test_name
    assert yourself['ready'] == test_ready
    assert yourself['admin'] == test_admin


def test_sanitize_retro_for_user_and_step():
    id = 'asdf-jkl'
    name = 'Sprint 28'
    current_step = RetroStep.ADDING_ISSUES.value
    user_token = 'whatever'
    participant = retro.create_mock_participant(token=user_token)
    a_retro = retro.create_mock_retro(id, name, current_step, participants=[participant])

    sanitized_retro = service.sanitize_retro_for_user_and_step(a_retro, user_token)

    assert sanitized_retro['id'] == id
    assert sanitized_retro['name'] == name
    assert sanitized_retro['currentStep'] == current_step
    assert sanitized_retro['participants'] is not None
    assert sanitized_retro['issues'] is not None
    assert sanitized_retro['yourself'] is not None


def test__create_participant():
    name = 'halprin'
    admin = True

    participant = service._create_participant(name, is_admin=admin)

    assert participant.name == name
    assert participant.admin is admin
    assert participant.ready is False
    assert participant.token is not None


@patch('backend.api.service._send_retro_update', autospec=True)
def test_add_participant(mock_send_retro_update):
    name = 'halprin'
    initial_participant_list = []
    a_retro = retro.create_mock_retro(participants=copy.deepcopy(initial_participant_list))

    user_token = service.add_participant(name, a_retro)

    assert len(a_retro.participants) == len(initial_participant_list) + 1
    assert user_token is not None
    assert user_token == a_retro.participants[len(a_retro.participants) - 1].token
    a_retro.save.assert_called_with()
    mock_send_retro_update.assert_called_once()


@patch('backend.api.service._send_retro_update', autospec=True)
def test_mark_user_as_ready(mock_send_retro_update):
    user_token = 'asdf-jkl'
    is_ready = True
    participants = [
        retro.create_mock_participant('DogCow', 'moof-token', ready=False),
        retro.create_mock_participant('halprin', user_token, ready=False)
    ]
    a_retro = retro.create_mock_retro(participants=participants)

    service.mark_user_as_ready(user_token, is_ready, a_retro)

    assert participants[0].ready is False
    assert participants[1].ready is is_ready
    a_retro.save.assert_called_with()
    mock_send_retro_update.assert_called_once()


def test__create_issue():
    title = 'improve code coverage'
    section = 'start doing'
    creator_token = 'asdf-jkl'

    actual = service._create_issue(title, section, creator_token)

    assert actual.title == title
    assert actual.section == section
    assert actual.creator_token == creator_token
    assert actual.votes is None
    assert actual.id is not None


@patch('backend.api.service._send_retro_update', autospec=True)
def test_add_new_issue(mock_send_retro_update):
    title = 'improve something'
    section = 'start doing'
    user_token = 'asdf-jkl'
    initial_issue_list = []
    a_retro = retro.create_mock_retro(issues=copy.deepcopy(initial_issue_list))

    actual_id = service.add_new_issue(title, section, user_token, a_retro)

    assert len(a_retro.issues) == len(initial_issue_list) + 1
    assert actual_id is not None
    assert actual_id == a_retro.issues[len(a_retro.issues) - 1].id
    a_retro.save.assert_called_with()
    mock_send_retro_update.assert_called_once()


@patch('backend.api.service._send_retro_update', autospec=True)
def test_vote_for_issue(mock_send_retro_update):
    issue_id_str = 'issue_id'
    user_token_str = 'voter_token'
    a_issue = retro.create_mock_issue(id=issue_id_str)
    a_retro = retro.create_mock_retro(issues=[a_issue])

    service.vote_for_issue(a_issue, user_token_str, a_retro)

    assert 1 == len(a_issue.votes)
    assert user_token_str in a_issue.votes
    mock_send_retro_update.assert_called_once()


@patch('backend.api.service._send_retro_update', autospec=True)
def test_vote_for_issue_twice_results_in_one_vote(mock_send_retro_update):
    issue_id_str = 'issue_id'
    user_token_str = 'voter_token'
    a_issue = retro.create_mock_issue(id=issue_id_str)
    a_retro = retro.create_mock_retro(issues=[a_issue])

    service.vote_for_issue(a_issue, user_token_str, a_retro)
    service.vote_for_issue(a_issue, user_token_str, a_retro)

    assert 1 == len(a_issue.votes)
    assert user_token_str in a_issue.votes
    assert 2 == mock_send_retro_update.call_count


def test_unvote_for_issue_with_no_votes():
    issue_id_str = 'issue_id'
    user_token_str = 'voter_token'
    a_issue = retro.create_mock_issue(id=issue_id_str)
    a_retro = retro.create_mock_retro(issues=[a_issue])

    service.unvote_for_issue(a_issue, user_token_str, a_retro)

    assert a_issue.votes is None or 0 == len(a_issue.votes)
    assert a_issue.votes is None or user_token_str not in a_issue.votes


@patch('backend.api.service._send_retro_update', autospec=True)
def test_unvote_for_issue(mock_send_retro_update):
    issue_id_str = 'issue_id'
    user_token_str = 'voter_token'
    a_issue = retro.create_mock_issue(id=issue_id_str, votes={user_token_str})
    a_retro = retro.create_mock_retro(issues=[a_issue])

    service.unvote_for_issue(a_issue, user_token_str, a_retro)

    assert a_issue.votes is None or 0 == len(a_issue.votes)
    assert a_issue.votes is None or user_token_str not in a_issue.votes
    mock_send_retro_update.assert_called_once()


@patch('backend.api.service._send_retro_update', autospec=True)
def test_unvote_for_issue_twice_results_in_zero_votes(mock_send_retro_update):
    issue_id_str = 'issue_id'
    user_token_str = 'voter_token'
    initial_votes = {user_token_str, 'another_voter_token'}
    initial_votes_length = len(initial_votes)
    a_issue = retro.create_mock_issue(id=issue_id_str, votes=initial_votes)
    a_retro = retro.create_mock_retro(issues=[a_issue])

    service.unvote_for_issue(a_issue, user_token_str, a_retro)
    service.unvote_for_issue(a_issue, user_token_str, a_retro)

    assert initial_votes_length - 1 == len(a_issue.votes)
    assert user_token_str not in a_issue.votes
    assert 2 == mock_send_retro_update.call_count


@patch('backend.api.service._send_retro_update', autospec=True)
def test_delete_issue(mock_send_retro_update):
    mock_issue = retro.create_mock_issue(id='some_issue')
    another_mock_issue = retro.create_mock_issue(id='another_issue')
    mock_retro = retro.create_mock_retro(issues=[another_mock_issue, mock_issue])

    service.delete_issue(mock_issue, mock_retro)

    assert mock_issue not in mock_retro.issues
    mock_send_retro_update.assert_called_once()


@patch('backend.api.service.async_to_sync', autospec=True)
@patch('backend.api.service.pickle', autospec=True)
@patch('backend.api.service.get_channel_layer', autospec=True)
def test__send_retro_update(mock_get_channel_layer_function, mock_pickle_module, mock_async_to_sync_function):
    mock_retro = retro.create_mock_retro()
    mock_channel_layer = MagicMock()
    mock_group_send = PropertyMock()
    type(mock_channel_layer).group_send = mock_group_send
    mock_get_channel_layer_function.return_value = mock_channel_layer

    service._send_retro_update(mock_retro)

    mock_get_channel_layer_function.assert_called_once()
    mock_group_send.assert_called_once()
