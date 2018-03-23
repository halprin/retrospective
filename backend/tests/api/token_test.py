from backend.api import token
from backend.tests.util import retro, request


def test_generate_token():
    new_token = token.generate_token()

    assert new_token is not None


def test_get_token_from_request():
    test_token = 'asdf-jkl'
    test_request = request.create_mock_request('', token=test_token)

    returned_token = token.get_token_from_request(test_request)

    assert test_token == returned_token


def test_token_is_valid_true():
    test_token = 'asdf-jkl'
    participant1 = retro.create_mock_participant(token='junk')
    participant2 = retro.create_mock_participant(token=test_token)
    a_retro = retro.create_mock_retro(participants=[participant1, participant2])

    result = token.token_is_valid(test_token, a_retro)

    assert result is True


def test_token_is_valid_false():
    participant1 = retro.create_mock_participant(token='junk')
    participant2 = retro.create_mock_participant(token='whatever')
    a_retro = retro.create_mock_retro(participants=[participant1, participant2])

    result = token.token_is_valid('something_not_above', a_retro)

    assert result is False


def test_token_is_admin_true():
    test_token = 'asdf-jkl'
    participant1 = retro.create_mock_participant(token='junk', admin=False)
    participant2 = retro.create_mock_participant(token=test_token, admin=True)
    a_retro = retro.create_mock_retro(participants=[participant1, participant2])

    result = token.token_is_admin(test_token, a_retro)

    assert result is True


def test_token_is_admin_false():
    test_token = 'asdf-jkl'
    participant1 = retro.create_mock_participant(token='junk', admin=False)
    participant2 = retro.create_mock_participant(token=test_token, admin=False)
    a_retro = retro.create_mock_retro(participants=[participant1, participant2])

    result = token.token_is_admin(test_token, a_retro)

    assert result is False


def test__find_participant_found():
    test_name = 'DogCow'
    participant1 = retro.create_mock_participant(name='lame_name')
    participant2 = retro.create_mock_participant(name=test_name)
    a_retro = retro.create_mock_retro(participants=[participant1, participant2])

    found_participant = token._find_participant(lambda participant: participant.name == test_name, a_retro)

    assert found_participant is participant2


def test__find_participant_none():
    participant1 = retro.create_mock_participant(name='lame_name')
    participant2 = retro.create_mock_participant(name='whatever_name')
    a_retro = retro.create_mock_retro(participants=[participant1, participant2])

    found_participant = token._find_participant(lambda participant: participant.name == 'something_not_above', a_retro)

    assert found_participant is None


def test_get_participant_found():
    test_token = 'asdf-jkl'
    participant1 = retro.create_mock_participant(token='junk')
    participant2 = retro.create_mock_participant(token=test_token)
    a_retro = retro.create_mock_retro(participants=[participant1, participant2])

    found_participant = token.get_participant(test_token, a_retro)

    assert found_participant is participant2


def test_get_participant_none():
    participant1 = retro.create_mock_participant(token='junk')
    participant2 = retro.create_mock_participant(token='whatever')
    a_retro = retro.create_mock_retro(participants=[participant1, participant2])

    found_participant = token.get_participant('something_not_above', a_retro)

    assert found_participant is None


def test_issue_owned_by_participant_negative():
    mock_issue = retro.create_mock_issue(creator_token='owner_id')

    issue_owned = token.issue_owned_by_participant(mock_issue, 'not_owner_id')

    assert issue_owned is False


def test_issue_owned_by_participant_positive():
    creator_token = 'owner_token'
    mock_issue = retro.create_mock_issue(creator_token=creator_token)

    issue_owned = token.issue_owned_by_participant(mock_issue, creator_token)

    assert issue_owned is True
