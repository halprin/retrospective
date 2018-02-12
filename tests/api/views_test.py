import json
from api.views import RetroView, RetroUserView, RetroIssueView
from api import views
from tests.util import request
from unittest.mock import patch
from tests.util import retro
from api.models import Retrospective, RetroStep


content_type = 'Content-Type'
content_type_application_json = 'application/json'


def assert_retro_not_found(response, retro_id):
    assert response.status_code == 404
    assert response[content_type] == views.content_type_text_plain
    assert response.charset == views.charset_utf8
    assert response.content.decode() == views.retro_not_found.format(retro_id)


def assert_user_not_valid(response):
    assert response.status_code == 401
    assert response[content_type] == views.content_type_text_plain
    assert response.charset == views.charset_utf8
    assert response.content.decode() == views.user_not_valid


@patch('api.views.token', autospec=True)
@patch('api.views.service', autospec=True)
class TestRetroView:
    def test_post_create_new_retro(self, mock_service, mock_token):
        request_body = {
            'retroName': 'Sprint 26',
            'adminName': 'halprin'
        }
        a_request = request.create_mock_request(request_body)
        new_retro_id = 'awesome_retro_id'
        new_admin_id = 'sweet_user_id'
        mock_new_retro = retro.create_mock_retro(id=new_retro_id, name=request_body['retroName'], participants=[
            retro.create_mock_participant(token=new_admin_id, name=request_body['adminName'], admin=True)])
        mock_service.create_retro.return_value = mock_new_retro

        object_under_test = RetroView()
        response = object_under_test.post(a_request)

        assert response.status_code == 201
        assert response[content_type] == content_type_application_json
        assert response.charset == views.charset_utf8
        assert json.loads(response.content) == {'retroId': new_retro_id, 'token': new_admin_id}

    def test_put_retro_doesnt_exist(self, mock_service, mock_token):
        request_body = {
            'direction': 'next'
        }
        mock_service.get_retro.side_effect = Retrospective.DoesNotExist

        object_under_test = RetroView()
        retro_id = 'non-existent_retro_id'
        response = object_under_test.put(request.create_mock_request(request_body), retro_id=retro_id)

        assert_retro_not_found(response, retro_id)

    def test_put_user_isnt_admin(self, mock_service, mock_token):
        request_body = {
            'direction': 'next'
        }
        mock_service.get_retro.return_value = retro.create_mock_retro()
        mock_token.token_is_admin.return_value = False

        object_under_test = RetroView()
        response = object_under_test.put(request.create_mock_request(request_body), retro_id='whatever')

        assert response.status_code == 401
        assert response[content_type] == views.content_type_text_plain
        assert response.charset == views.charset_utf8
        assert response.content.decode() == views.user_not_admin

    def test_put_move_isnt_allowed(self, mock_service, mock_token):
        request_body = {
            'direction': 'next'
        }
        mock_service.get_retro.return_value = retro.create_mock_retro()
        mock_token.token_is_admin.return_value = True
        value_error_text = "Can't move that direction"
        mock_service.move_retro.side_effect = ValueError(value_error_text)

        object_under_test = RetroView()
        response = object_under_test.put(request.create_mock_request(request_body), retro_id='whatever')

        assert response.status_code == 422
        assert response[content_type] == views.content_type_text_plain
        assert response.charset == views.charset_utf8
        assert response.content.decode() == value_error_text

    def test_put_move_success(self, mock_service, mock_token):
        request_body = {
            'direction': 'next'
        }
        mock_service.get_retro.return_value = retro.create_mock_retro()
        mock_token.token_is_admin.return_value = True
        new_stage = "Voting"
        mock_service.move_retro.return_value = new_stage

        object_under_test = RetroView()
        response = object_under_test.put(request.create_mock_request(request_body), retro_id='whatever')

        assert response.status_code == 200
        assert response[content_type] == content_type_application_json
        assert response.charset == views.charset_utf8
        assert json.loads(response.content) == {'newStep': new_stage}

    def test_get_retro_doesnt_exist(self, mock_service, mock_token):
        mock_service.get_retro.side_effect = Retrospective.DoesNotExist

        object_under_test = RetroView()
        retro_id = 'non-existent_retro_id'
        response = object_under_test.get(request.create_mock_request(), retro_id=retro_id)

        assert_retro_not_found(response, retro_id)

    def test_get_user_isnt_valid(self, mock_service, mock_token):
        mock_service.get_retro.return_value = retro.create_mock_retro()
        mock_token.token_is_valid.return_value = False

        object_under_test = RetroView()
        response = object_under_test.get(request.create_mock_request(), retro_id='whatever')

        assert_user_not_valid(response)

    def test_get_retro_success(self, mock_service, mock_token):
        mock_service.get_retro.return_value = retro.create_mock_retro()
        mock_token.token_is_valid.return_value = True
        mock_response = {'mockResponseBody': 'one awesome response body'}
        mock_service.sanitize_retro_for_user_and_step.return_value = mock_response

        object_under_test = RetroView()
        response = object_under_test.get(request.create_mock_request(), retro_id='whatever')

        assert response.status_code == 200
        assert response[content_type] == content_type_application_json
        assert response.charset == views.charset_utf8
        assert json.loads(response.content) == mock_response


@patch('api.views.token', autospec=True)
@patch('api.views.service', autospec=True)
class TestRetroUserView:
    def test_post_retro_not_found(self, mock_service, mock_token):
        mock_service.get_retro.side_effect = Retrospective.DoesNotExist

        object_under_test = RetroUserView()
        retro_id = 'non-existent_retro_id'
        response = object_under_test.post(request.create_mock_request(), retro_id=retro_id)

        assert_retro_not_found(response, retro_id)

    def test_post_new_user_success(self, mock_service, mock_token):
        request_body = {
            'name': 'new_user'
        }
        mock_service.get_retro.return_value = retro.create_mock_retro()
        new_user_token = 'a-special-new-token'
        mock_service.add_participant.return_value = new_user_token

        object_under_test = RetroUserView()
        retro_id = 'whatever_retro_id'
        response = object_under_test.post(request.create_mock_request(request_body), retro_id=retro_id)

        assert response.status_code == 201
        assert response[content_type] == content_type_application_json
        assert response.charset == views.charset_utf8
        assert json.loads(response.content) == {'token': new_user_token}

    def test_put_retro_not_found(self, mock_service, mock_token):
        mock_service.get_retro.side_effect = Retrospective.DoesNotExist

        object_under_test = RetroUserView()
        retro_id = 'non-existent_retro_id'
        response = object_under_test.put(request.create_mock_request(), retro_id=retro_id)

        assert_retro_not_found(response, retro_id)

    def test_put_user_not_valid(self, mock_service, mock_token):
        mock_service.get_retro.return_value = retro.create_mock_retro()
        mock_token.token_is_valid.return_value = False

        object_under_test = RetroUserView()
        response = object_under_test.put(request.create_mock_request(), retro_id='whatever')

        assert_user_not_valid(response)

    def test_put_user_ready_success_true(self, mock_service, mock_token):
        request_body = {
            'ready': True
        }
        mock_service.get_retro.return_value = retro.create_mock_retro()
        mock_token.token_is_valid.return_value = True

        object_under_test = RetroUserView()
        response = object_under_test.put(request.create_mock_request(request_body), retro_id='whatever')

        assert response.status_code == 200
        assert response[content_type] == views.content_type_text_plain
        assert response.charset == views.charset_utf8
        assert response.content.decode() == ''


@patch('api.views.token', autospec=True)
@patch('api.views.service', autospec=True)
class TestRetroIssueView:
    def test_post_retro_not_found(self, mock_service, mock_token):
        mock_service.get_retro.side_effect = Retrospective.DoesNotExist

        object_under_test = RetroIssueView()
        retro_id = 'non-existent_retro_id'
        response = object_under_test.post(request.create_mock_request(), retro_id=retro_id)

        assert_retro_not_found(response, retro_id)

    def test_post_user_not_valid(self, mock_service, mock_token):
        mock_service.get_retro.return_value = retro.create_mock_retro()
        mock_token.token_is_valid.return_value = False

        object_under_test = RetroIssueView()
        response = object_under_test.post(request.create_mock_request(), retro_id='whatever')

        assert_user_not_valid(response)

    def test_post_retro_step_not_valid(self, mock_service, mock_token):
        retro_step = RetroStep.VOTING.value
        mock_service.get_retro.return_value = retro.create_mock_retro(current_step=retro_step)
        mock_token.token_is_valid.return_value = True

        object_under_test = RetroIssueView()
        response = object_under_test.post(request.create_mock_request(), retro_id='whatever')

        assert response.status_code == 422
        assert response[content_type] == views.content_type_text_plain
        assert response.charset == views.charset_utf8
        assert response.content.decode() == views.no_create_issue_retro_wrong_step.format(retro_step)

    def test_post_new_issue_success(self, mock_service, mock_token):
        request_body = {
            'title': 'More timely PR reviews',
            'section': 'Needs Improvement'
        }
        mock_service.get_retro.return_value = retro.create_mock_retro()
        mock_token.token_is_valid.return_value = True
        mock_issue_id = 'new_issue_id'
        mock_service.add_new_issue.return_value = mock_issue_id

        object_under_test = RetroIssueView()
        response = object_under_test.post(request.create_mock_request(request_body), retro_id='whatever')

        assert response.status_code == 201
        assert response[content_type] == content_type_application_json
        assert response.charset == views.charset_utf8
        assert json.loads(response.content) == {'id': mock_issue_id}

    def test_put_retro_not_found(self, mock_service, mock_token):
        mock_service.get_retro.side_effect = Retrospective.DoesNotExist

        object_under_test = RetroIssueView()
        retro_id = 'non-existent_retro_id'
        response = object_under_test.put(request.create_mock_request(), retro_id=retro_id, issue_id='some_issue_id')

        assert_retro_not_found(response, retro_id)

    def test_put_user_not_valid(self, mock_service, mock_token):
        mock_service.get_retro.return_value = retro.create_mock_retro()
        mock_token.token_is_valid.return_value = False

        object_under_test = RetroIssueView()
        response = object_under_test.put(request.create_mock_request(), retro_id='whatever', issue_id='some_issue_id')

        assert_user_not_valid(response)

    def test_put_retro_not_voting_step(self, mock_service, mock_token):
        incorrect_retro_step = RetroStep.ADDING_ISSUES.value
        mock_service.get_retro.return_value = retro.create_mock_retro(current_step=incorrect_retro_step)
        mock_token.token_is_valid.return_value = True

        object_under_test = RetroIssueView()
        response = object_under_test.put(request.create_mock_request(), retro_id='whatever', issue_id='some_issue_id')

        assert response.status_code == 422
        assert response[content_type] == views.content_type_text_plain
        assert response.charset == views.charset_utf8
        assert response.content.decode() == views.no_vote_issue_retro_wrong_step.format(incorrect_retro_step)

    def test_put_retro_success(self, mock_service, mock_token):
        mock_service.get_retro.return_value = retro.create_mock_retro(current_step=RetroStep.VOTING.value)
        mock_token.token_is_valid.return_value = True

        object_under_test = RetroIssueView()
        response = object_under_test.put(request.create_mock_request(), retro_id='whatever', issue_id='some_issue_id')

        assert response.status_code == 200
        assert response[content_type] == views.content_type_text_plain
        assert response.charset == views.charset_utf8
        assert response.content.decode() == ''
