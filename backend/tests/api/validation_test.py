from unittest.mock import patch
from backend.api import validation
from backend.api.models import Retrospective, RetroStep
from backend.tests.util import retro, validators, request


def original_function(*args, **kwargs):
    return {
        'args': args,
        'kwargs': kwargs
    }


@patch('backend.api.validation.service', autospec=True)
def test_retrospective_exists_negative(mock_service):
    mock_service.get_retro.side_effect = Retrospective.DoesNotExist

    retro_id = 'non-existent_retro_id'
    object_under_test = validation.retrospective_exists(original_function)
    response = object_under_test(retro_id=retro_id)

    validators.assert_retro_not_found(response, retro_id)


@patch('backend.api.validation.service', autospec=True)
def test_retrospective_exists_positive(mock_service):
    mock_retro = retro.create_mock_retro()
    mock_service.get_retro.return_value = mock_retro

    passed_in_retro_id = 'some_retro_id'
    object_under_test = validation.retrospective_exists(original_function)
    passed_args = object_under_test(retro_id=passed_in_retro_id)

    assert mock_retro == passed_args['kwargs']['retro']
    assert passed_in_retro_id == passed_args['kwargs']['retro_id']


@patch('backend.api.validation.token', autospec=True)
def test_user_is_admin_negative(mock_token):
    mock_token.token_is_admin.return_value = False

    object_under_test = validation.user_is_admin(original_function)
    response = object_under_test(None, request.create_mock_request(), retro=retro.create_mock_retro())

    validators.assert_user_not_admin(response)


@patch('backend.api.validation.token', autospec=True)
def test_user_is_admin_positive(mock_token):
    mock_token.token_is_admin.return_value = True
    mock_retro = retro.create_mock_retro()
    mock_request = request.create_mock_request()

    object_under_test = validation.user_is_admin(original_function)
    passed_args = object_under_test(None, mock_request, retro=mock_retro)

    assert mock_request == passed_args['args'][1]
    assert mock_retro == passed_args['kwargs']['retro']


@patch('backend.api.validation.token', autospec=True)
def test_user_is_valid_negative(mock_token):
    mock_token.token_is_valid.return_value = False

    object_under_test = validation.user_is_valid(original_function)
    response = object_under_test(None, request.create_mock_request(), retro=retro.create_mock_retro())

    validators.assert_user_not_valid(response)


@patch('backend.api.validation.token', autospec=True)
def test_user_is_valid_positive(mock_token):
    mock_token.token_is_valid.return_value = True
    mock_retro = retro.create_mock_retro()
    mock_request = request.create_mock_request()

    object_under_test = validation.user_is_valid(original_function)
    passed_args = object_under_test(None, mock_request, retro=mock_retro)

    assert mock_request == passed_args['args'][1]
    assert mock_retro == passed_args['kwargs']['retro']


def test_retro_on_step_negative():
    error_message = 'Some test {}'
    retro_step = RetroStep.ADDING_ISSUES.value
    object_under_test = validation.retro_on_step(RetroStep.VOTING, error_message)(original_function)

    response = object_under_test(retro=retro.create_mock_retro(current_step=retro_step))

    validators.assert_retro_not_on_step(response, error_message.format(retro_step))


def test_retro_on_step_positive():
    retro_step = RetroStep.VOTING
    mock_retro = retro.create_mock_retro(current_step=retro_step.value)
    object_under_test = validation.retro_on_step(retro_step, 'Some test {}')(original_function)

    passed_args = object_under_test(retro=mock_retro)

    assert mock_retro == passed_args['kwargs']['retro']
