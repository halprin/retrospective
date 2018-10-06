from backend.api.serviceV2 import ServiceV2
from backend.tests.util import retro
from backend.api.modelsV2 import RetroStepV2
from unittest.mock import patch
import pytest


@patch('backend.api.serviceV2.RetrospectiveV2', autospec=True)
def test_create_retro(mock_retrospective_class):
    retro_name = 'Sprint 26'
    admin_name = 'DogCow'
    mock_retrospective_class.side_effect = lambda retro_id: retro.create_mock_retroV2(id=retro_id)

    new_retro = ServiceV2.create_retro(retro_name, admin_name)

    assert new_retro.name == retro_name
    assert new_retro.current_step == RetroStepV2.ADDING_ISSUES.value
    assert len(new_retro.participants) == 1
    assert new_retro.participants[0].name == admin_name
    assert new_retro.participants[0].admin is True
    assert len(new_retro.issues) == 0
    assert len(new_retro.groups) == 0
    assert new_retro.version == '2'
    assert new_retro.id is not None


@patch('backend.api.serviceV2.RetrospectiveV2', autospec=True)
def test_get_retro(mock_retrospective_class):
    retro_id = 'an_awesome_retro_id'
    mock_retrospective_class.get.side_effect = lambda passed_in_retro_id: retro.create_mock_retroV2(
        id=passed_in_retro_id)

    returned_retro = ServiceV2.get_retro(retro_id)

    mock_retrospective_class.get.assert_called_with(retro_id)
    assert returned_retro.id == retro_id


def test__get_retro_step():
    assert ServiceV2._get_retro_step(RetroStepV2.GROUPING.value) is RetroStepV2.GROUPING


def test__is_adding_issues_step():
    assert ServiceV2._is_adding_issues_step(RetroStepV2.VOTING) is False
    assert ServiceV2._is_adding_issues_step(RetroStepV2.ADDING_ISSUES) is True


def test__is_grouping_step():
    assert ServiceV2._is_grouping_step(RetroStepV2.VOTING) is False
    assert ServiceV2._is_grouping_step(RetroStepV2.GROUPING) is True


def test__is_voting_step():
    assert ServiceV2._is_voting_step(RetroStepV2.RESULTS) is False
    assert ServiceV2._is_voting_step(RetroStepV2.VOTING) is True


def test__is_results_step():
    assert ServiceV2._is_results_step(RetroStepV2.VOTING) is False
    assert ServiceV2._is_results_step(RetroStepV2.RESULTS) is True


def test__sanitize_issue():
    mock_group = 'Moof'
    mock_issue = retro.create_mock_issueV2(group=mock_group)

    actual_sanitized_issue = ServiceV2._sanitize_issue(mock_issue, RetroStepV2.ADDING_ISSUES, 'whatever-user-token')

    assert mock_group == actual_sanitized_issue['group']


def test__sanitize_group_adding_issues_step():
    mock_id = 'DogCow'
    mock_title = 'Moof'
    mock_section = 'Some cool section'
    mock_user_token = 'voter1_is_cool'
    mock_votes = [mock_user_token, 'voter2']

    mock_group = retro.create_mock_group(id=mock_id, title=mock_title, section=mock_section, votes=mock_votes)

    actual_sanitized_group = ServiceV2._sanitize_group(mock_group, RetroStepV2.ADDING_ISSUES, mock_user_token)

    assert mock_id == actual_sanitized_group['id']
    assert mock_title == actual_sanitized_group['title']
    assert mock_section == actual_sanitized_group['section']
    with pytest.raises(KeyError):
        actual_sanitized_group['votes']


def test__sanitize_group_grouping_step():
    mock_id = 'DogCow'
    mock_title = 'Moof'
    mock_section = 'Some cool section'
    mock_user_token = 'voter1_is_cool'
    mock_votes = [mock_user_token, 'voter2']

    mock_group = retro.create_mock_group(id=mock_id, title=mock_title, section=mock_section, votes=mock_votes)

    actual_sanitized_group = ServiceV2._sanitize_group(mock_group, RetroStepV2.GROUPING, mock_user_token)

    assert mock_id == actual_sanitized_group['id']
    assert mock_title == actual_sanitized_group['title']
    assert mock_section == actual_sanitized_group['section']
    with pytest.raises(KeyError):
        actual_sanitized_group['votes']


def test__sanitize_group_voting_step():
    mock_id = 'DogCow'
    mock_title = 'Moof'
    mock_section = 'Some cool section'
    mock_user_token = 'voter1_is_cool'
    mock_votes = [mock_user_token, 'voter2']

    mock_group = retro.create_mock_group(id=mock_id, title=mock_title, section=mock_section, votes=mock_votes)

    actual_sanitized_group = ServiceV2._sanitize_group(mock_group, RetroStepV2.VOTING, mock_user_token)

    assert mock_id == actual_sanitized_group['id']
    assert mock_title == actual_sanitized_group['title']
    assert mock_section == actual_sanitized_group['section']
    assert 1 == actual_sanitized_group['votes']


def test__sanitize_group_results_step():
    mock_id = 'DogCow'
    mock_title = 'Moof'
    mock_section = 'Some cool section'
    mock_user_token = 'voter1_is_cool'
    mock_votes = [mock_user_token, 'voter2']

    mock_group = retro.create_mock_group(id=mock_id, title=mock_title, section=mock_section, votes=mock_votes)

    actual_sanitized_group = ServiceV2._sanitize_group(mock_group, RetroStepV2.RESULTS, mock_user_token)

    assert mock_id == actual_sanitized_group['id']
    assert mock_title == actual_sanitized_group['title']
    assert mock_section == actual_sanitized_group['section']
    assert len(mock_votes) == actual_sanitized_group['votes']


def test__sanitize_group_list():
    size = 4

    groups = [retro.create_mock_group(id='id' + str(index)) for index in range(size)]
    mock_retro = retro.create_mock_retroV2(groups=groups)

    sanitized_groups = ServiceV2._sanitize_group_list(mock_retro, 'user-token')

    assert size == len(sanitized_groups)


def test_sanitize_retro_for_user_and_step():
    size = 4
    mock_user_token = 'user-token'
    mock_id = 'crazy_id'
    mock_name = 'Moof!'

    groups = [retro.create_mock_group(id='id'+str(index))for index in range(size)]

    mock_retro = retro.create_mock_retroV2(id=mock_id, name=mock_name, groups=groups,
                                           issues=[retro.create_mock_issueV2()],
                                           participants=[retro.create_mock_participant(token=mock_user_token)])

    sanitized_retro = ServiceV2.sanitize_retro_for_user_and_step(mock_retro, mock_user_token)

    assert mock_id == sanitized_retro['id']
    assert mock_name == sanitized_retro['name']
    assert len(mock_retro.participants) == len(sanitized_retro['participants'])
    assert len(mock_retro.issues) == len(sanitized_retro['issues'])
    assert size == len(sanitized_retro['groups'])
    assert 'yourself' in sanitized_retro


def test__create_issue():
    title = 'a title'
    section = 'a section'
    owner = 'a token'

    issue = ServiceV2._create_issue(title, section, owner)

    assert title == issue.title
    assert section == issue.section
    assert owner == issue.creator_token
    assert issue.votes is None
    assert issue.group is None


def test__get_group_by_id():
    mock_id = 'a great id'

    mock_retro = retro.create_mock_retroV2(groups=[retro.create_mock_group(id='whatever'), retro.create_mock_group(id=mock_id)])

    found_group = ServiceV2._get_group_by_id(mock_id, mock_retro)

    assert found_group is not None
    assert mock_id == found_group.id


def test__get_group_by_id_not_found():
    mock_id = 'a great id'

    mock_retro = retro.create_mock_retroV2(groups=[retro.create_mock_group(id='whatever'), retro.create_mock_group(id='another whatever')])

    found_group = ServiceV2._get_group_by_id(mock_id, mock_retro)

    assert found_group is None


@patch('backend.api.service.Service._send_retro_update')
def test_vote_for_issue_non_group(mock_send_retro_update):

    voting_user = 'user-token'

    mock_group = retro.create_mock_group(id='a group')
    mock_issue = retro.create_mock_issueV2(id='an issue', group='')
    mock_retro = retro.create_mock_retroV2(id='a retro', issues=[mock_issue], groups=[mock_group])

    ServiceV2.vote_for_issue(mock_issue, voting_user, mock_retro)

    assert voting_user in mock_issue.votes
    assert mock_group.votes is None or voting_user not in mock_group.votes


@patch('backend.api.service.Service._send_retro_update')
def test_vote_for_issue_for_group(mock_send_retro_update):

    voting_user = 'user-token'

    mock_group = retro.create_mock_group(id='a group')
    mock_issue = retro.create_mock_issueV2(id='an issue', group=mock_group.id)
    mock_retro = retro.create_mock_retroV2(id='a retro', issues=[mock_issue], groups=[mock_group])

    ServiceV2.vote_for_issue(mock_issue, voting_user, mock_retro)

    assert mock_issue.votes is None or voting_user not in mock_issue.votes
    assert voting_user in mock_group.votes


@patch('backend.api.service.Service._send_retro_update')
def test_vote_for_group(mock_send_retro_update):
    voting_user = 'user-token'

    mock_group = retro.create_mock_group(id='a group')
    mock_retro = retro.create_mock_retroV2(id='a retro', groups=[mock_group])

    ServiceV2.vote_for_group(mock_group, voting_user, mock_retro)

    assert voting_user in mock_group.votes


@patch('backend.api.service.Service._send_retro_update')
def test_unvote_for_issue_non_group(mock_send_retro_update):

    voting_user = 'user-token'

    mock_group = retro.create_mock_group(id='a group')
    mock_issue = retro.create_mock_issueV2(id='an issue', group='', votes={voting_user})
    mock_retro = retro.create_mock_retroV2(id='a retro', issues=[mock_issue], groups=[mock_group])

    ServiceV2.unvote_for_issue(mock_issue, voting_user, mock_retro)

    assert mock_issue.votes is None or voting_user not in mock_issue.votes
    assert mock_group.votes is None or voting_user not in mock_group.votes


@patch('backend.api.service.Service._send_retro_update')
def test_unvote_for_issue_for_group(mock_send_retro_update):

    voting_user = 'user-token'

    mock_group = retro.create_mock_group(id='a group', votes={voting_user})
    mock_issue = retro.create_mock_issueV2(id='an issue', group=mock_group.id)
    mock_retro = retro.create_mock_retroV2(id='a retro', issues=[mock_issue], groups=[mock_group])

    ServiceV2.unvote_for_issue(mock_issue, voting_user, mock_retro)

    assert mock_issue.votes is None or voting_user not in mock_issue.votes
    assert mock_group.votes is None or voting_user not in mock_group.votes


@patch('backend.api.service.Service._send_retro_update')
def test_unvote_for_group(mock_send_retro_update):
    voting_user = 'user-token'

    mock_group = retro.create_mock_group(id='a group', votes={voting_user})
    mock_retro = retro.create_mock_retroV2(id='a retro', groups=[mock_group])

    ServiceV2.unvote_for_group(mock_group, voting_user, mock_retro)

    assert mock_group.votes is None or voting_user not in mock_group.votes


@patch('backend.api.service.Service._send_retro_update')
def test_group_issue(mock_send_retro_update):
    mock_group = retro.create_mock_group(id='a group')
    mock_issue = retro.create_mock_issueV2(id='an issue')
    mock_retro = retro.create_mock_retroV2(id='a retro', issues=[mock_issue], groups=[mock_group])

    ServiceV2.group_issue(mock_issue, mock_group, mock_retro)

    assert mock_group.id == mock_issue.group


@patch('backend.api.service.Service._send_retro_update')
def test_ungroup_issue(mock_send_retro_update):
    mock_group = retro.create_mock_group(id='a group')
    mock_issue = retro.create_mock_issueV2(id='an issue', group=mock_group.id)
    mock_retro = retro.create_mock_retroV2(id='a retro', issues=[mock_issue], groups=[mock_group])

    ServiceV2.ungroup_issue(mock_issue, mock_retro)

    assert mock_issue.group is None


@patch('backend.api.service.Service._send_retro_update')
def test_add_new_group(mock_send_retro_update):
    mock_group_title = 'group_moof'
    mock_group_section = 'a_section'
    mock_retro = retro.create_mock_retroV2()

    ServiceV2.add_new_group(mock_group_title, mock_group_section, mock_retro)

    assert mock_retro.groups is not None
    assert 1 == len(mock_retro.groups)
    assert mock_group_title == mock_retro.groups[0].title
    assert mock_group_section == mock_retro.groups[0].section
    assert mock_retro.groups[0].votes is None or 0 == len(mock_retro.groups[0].votes)
    assert mock_retro.groups[0].id is not None and 0 != len(mock_retro.groups[0].id)


@patch('backend.api.service.Service._send_retro_update')
def test_delete_group(mock_send_retro_update):
    mock_group1 = retro.create_mock_group(id='group1')
    mock_group2 = retro.create_mock_group(id='group2')
    mock_issue1 = retro.create_mock_issueV2(group=mock_group1.id)
    mock_issue2 = retro.create_mock_issueV2()
    mock_issue3 = retro.create_mock_issueV2(group=mock_group2.id)
    mock_issue4 = retro.create_mock_issueV2(group=mock_group1.id)
    mock_retro = retro.create_mock_retroV2(groups=[mock_group1, mock_group2], issues=[mock_issue1, mock_issue2, mock_issue3, mock_issue4])

    before_group_number = len(mock_retro.groups)

    ServiceV2.delete_group(mock_group1, mock_retro)

    assert before_group_number - 1 == len(mock_retro.groups)
    assert mock_issue1.group is None
    assert mock_issue4.group is None
    assert mock_group2.id == mock_issue3.group
