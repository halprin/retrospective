from backend.api import validation
from backend.tests.util import request, retro
from backend.api.models import Retrospective
from pynamodb.models import Model


content_type = 'Content-Type'


def assert_retro_not_found(response, retro_id):
    assert 404 == response.status_code
    assert validation.content_type_text_plain == response.headers['Content-Type']
    assert validation.retro_not_found.format(retro_id) == response.body


def assert_user_not_admin(response):
    assert 401 == response.status_code
    assert validation.content_type_text_plain == response.headers['Content-Type']
    assert validation.user_not_admin == response.body


def assert_user_not_valid(response):
    assert 401 == response.status_code
    assert validation.content_type_text_plain == response.headers['Content-Type']
    assert validation.user_not_valid == response.body


def assert_retro_not_on_step(response, expected_error_message):
    assert 422 == response.status_code
    assert validation.content_type_text_plain == response.headers['Content-Type']
    assert expected_error_message == response.body


def assert_issue_not_found(response, issue_id):
    assert 404 == response.status_code
    assert validation.content_type_text_plain == response.headers['Content-Type']
    assert validation.issue_not_found.format(issue_id) == response.body


def assert_user_not_owner_of_issue(response, issue_id):
    assert 401 == response.status_code
    assert validation.content_type_text_plain == response.headers['Content-Type']
    assert validation.user_is_not_issue_owner.format(issue_id) == response.body


def assert_api_mismatch(response, api_version, retro_version):
    assert 409 == response.status_code
    assert validation.content_type_text_plain == response.headers['Content-Type']
    assert validation.incorrect_api_version.format(api_version, retro_version) == response.body


def assert_group_not_found(response, group_id):
    assert 404 == response.status_code
    assert validation.content_type_text_plain == response.headers['Content-Type']
    assert validation.group_not_found.format(group_id) == response.body


def assert_function_returns_retrospective_does_not_exist(function, mock_service_function_validation):

    mock_service_function_validation.return_value.get_retro.side_effect = Model.DoesNotExist

    request_body = {
        'does': 'nothing'
    }
    retro_id = 'non-existent_retro_id'

    response = function(request.create_mock_request(request_body, retro_id=retro_id))

    assert_retro_not_found(response, retro_id)


def assert_function_returns_api_mismatch(function, mock_service_function_validation, mock_retro: Retrospective):
    request_body = {
        'does': 'nothing'
    }
    mock_service_function_validation.return_value.get_retro.return_value = mock_retro
    mock_api_version = 'incorrect_version'
    mock_request = request.create_mock_request(request_body, retro_id='whatever', api_version=mock_api_version)

    response = function(mock_request)

    assert_api_mismatch(response, mock_api_version, mock_retro.version)


def assert_function_returns_user_not_valid(function, mock_service_function_validation, mock_token, mock_retro):
    mock_service_function_validation.return_value.get_retro.return_value = mock_retro
    mock_token.token_is_valid.return_value = False

    response = function(request.create_mock_request(retro_id='whatever', api_version=mock_retro.version))

    assert_user_not_valid(response)


def assert_function_returns_retro_not_on_step(function, mock_service_function_validation, mock_token, mock_retro,
                                              expected_error_message):
    mock_service_function_validation.return_value.get_retro.return_value = mock_retro
    mock_token.token_is_valid.return_value = True

    response = function(request.create_mock_request(retro_id='whatever', api_version=mock_retro.version))

    assert_retro_not_on_step(response, expected_error_message)


def assert_function_returns_group_not_found(function, mock_service_function_validation, mock_token, mock_retro):
    mock_service_function_validation.return_value.get_retro.return_value = mock_retro
    mock_token.token_is_valid.return_value = True
    mock_retro.groups.append(retro.create_mock_group(id='a_group'))
    non_existing_group_id = 'non-existing_group_id'

    response = function(request.create_mock_request(retro_id='whatever', group_id=non_existing_group_id,
                                                    api_version=mock_retro.version))

    assert_group_not_found(response, non_existing_group_id)

