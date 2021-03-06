import json
from backend.api.views.views import RetroView, RetroUserView, RetroIssueView
from backend.api.views import views
from unittest.mock import patch
from backend.tests.util import retro, request, validators
from backend.api.models import RetroStep


content_type_application_json = 'application/json'


@patch('backend.api.validation.token', autospec=True)
@patch('backend.api.views.views.Service', autospec=True)
@patch('backend.api.validation._get_service', autospec=True)
class TestRetroView:
    def test_post_create_new_retro(self, mock_service_validation, mock_service_view, mock_token):
        request_body = {
            'retroName': 'Sprint 26',
            'adminName': 'halprin'
        }
        a_request = request.create_mock_request(request_body)
        new_retro_id = 'awesome_retro_id'
        new_admin_id = 'sweet_user_id'
        mock_new_retro = retro.create_mock_retro(id=new_retro_id, name=request_body['retroName'], participants=[
            retro.create_mock_participant(token=new_admin_id, name=request_body['adminName'], admin=True)])
        mock_service_view.create_retro.return_value = mock_new_retro

        object_under_test = RetroView()
        response = object_under_test.post(a_request)

        assert response.status_code == 201
        assert response.headers[validators.content_type] == content_type_application_json
        assert json.loads(response.body) == {'retroId': new_retro_id, 'token': new_admin_id}

    def test_put_retro_doesnt_exist(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroView()
        validators.assert_function_returns_retrospective_does_not_exist(object_under_test.put,
                                                                        mock_service_function_validation)

    def test_put_api_mismatch(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroView()
        validators.assert_function_returns_api_mismatch(object_under_test.put, mock_service_function_validation,
                                                        retro.create_mock_retro())

    def test_put_user_isnt_admin(self, mock_service_function_validation, mock_service_view, mock_token):
        request_body = {
            'direction': 'next'
        }
        mock_service_function_validation.return_value.get_retro.return_value = retro.create_mock_retro(id='moof')
        mock_token.token_is_admin.return_value = False

        object_under_test = RetroView()
        response = object_under_test.put(request.create_mock_request(request_body, retro_id='whatever'))

        validators.assert_user_not_admin(response)

    def test_put_move_isnt_allowed(self, mock_service_function_validation, mock_service_view, mock_token):
        request_body = {
            'direction': 'next'
        }
        mock_service_function_validation.return_value.get_retro.return_value = retro.create_mock_retro()
        mock_token.token_is_admin.return_value = True
        value_error_text = "Can't move that direction"
        mock_service_view.move_retro.side_effect = ValueError(value_error_text)

        object_under_test = RetroView()
        response = object_under_test.put(request.create_mock_request(request_body,retro_id='whatever'))

        assert response.status_code == 422
        assert response.headers[validators.content_type] == views.content_type_text_plain
        assert response.body == value_error_text

    def test_put_move_success(self, mock_service_function_validation, mock_service_view, mock_token):
        request_body = {
            'direction': 'next'
        }
        mock_service_function_validation.return_value.get_retro.return_value = retro.create_mock_retro()
        mock_token.token_is_admin.return_value = True
        new_stage = 'Voting'
        mock_service_view.move_retro.return_value = new_stage

        object_under_test = RetroView()
        response = object_under_test.put(request.create_mock_request(request_body, retro_id='whatever'))

        assert response.status_code == 200
        assert response.headers[validators.content_type] == content_type_application_json
        assert json.loads(response.body) == {'newStep': new_stage}

    def test_get_retro_doesnt_exist(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroView()
        validators.assert_function_returns_retrospective_does_not_exist(object_under_test.get,
                                                                        mock_service_function_validation)

    def test_get_api_mismatch(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroView()
        validators.assert_function_returns_api_mismatch(object_under_test.get, mock_service_function_validation,
                                                        retro.create_mock_retro())

    def test_get_user_isnt_valid(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroView()
        validators.assert_function_returns_user_not_valid(object_under_test.get, mock_service_function_validation,
                                                          mock_token, retro.create_mock_retro())

    def test_get_retro_success(self, mock_service_function_validation, mock_service_view, mock_token):
        mock_service_function_validation.return_value.get_retro.return_value = retro.create_mock_retro()
        mock_token.token_is_valid.return_value = True
        mock_response = {'mockResponseBody': 'one awesome response body'}
        mock_service_view.sanitize_retro_for_user_and_step.return_value = mock_response

        object_under_test = RetroView()
        response = object_under_test.get(request.create_mock_request(retro_id='whatever'))

        assert response.status_code == 200
        assert response.headers[validators.content_type] == content_type_application_json
        assert json.loads(response.body) == mock_response


@patch('backend.api.validation.token', autospec=True)
@patch('backend.api.views.views.Service', autospec=True)
@patch('backend.api.validation._get_service', autospec=True)
class TestRetroUserView:
    def test_post_retro_not_found(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroUserView()
        validators.assert_function_returns_retrospective_does_not_exist(object_under_test.post,
                                                                        mock_service_function_validation)

    def test_post_api_mismatch(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroUserView()
        validators.assert_function_returns_api_mismatch(object_under_test.post, mock_service_function_validation,
                                                        retro.create_mock_retro())

    def test_post_new_user_success(self, mock_service_function_validation, mock_service_view, mock_token):
        request_body = {
            'name': 'new_user'
        }
        mock_service_function_validation.return_value.get_retro.return_value = retro.create_mock_retro()
        new_user_token = 'a-special-new-token'
        mock_service_view.add_participant.return_value = new_user_token

        object_under_test = RetroUserView()
        retro_id = 'whatever_retro_id'
        response = object_under_test.post(request.create_mock_request(request_body, retro_id=retro_id))

        assert response.status_code == 201
        assert response.headers[validators.content_type] == content_type_application_json
        assert json.loads(response.body) == {'token': new_user_token}

    def test_put_retro_not_found(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroUserView()
        validators.assert_function_returns_retrospective_does_not_exist(object_under_test.put,
                                                                        mock_service_function_validation)

    def test_put_api_mismatch(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroUserView()
        validators.assert_function_returns_api_mismatch(object_under_test.put, mock_service_function_validation,
                                                        retro.create_mock_retro())

    def test_put_user_not_valid(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroUserView()
        validators.assert_function_returns_user_not_valid(object_under_test.put, mock_service_function_validation,
                                                          mock_token, retro.create_mock_retro())

    def test_put_user_ready_success_true(self, mock_service_function_validation, mock_service_view, mock_token):
        request_body = {
            'ready': True
        }
        mock_service_function_validation.return_value.get_retro.return_value = retro.create_mock_retro()
        mock_token.token_is_valid.return_value = True

        object_under_test = RetroUserView()
        response = object_under_test.put(request.create_mock_request(request_body, retro_id='whatever'))

        assert response.status_code == 200
        assert response.headers[validators.content_type] == views.content_type_text_plain
        assert response.body == ''


@patch('backend.api.validation.token', autospec=True)
@patch('backend.api.views.views.Service', autospec=True)
@patch('backend.api.validation._get_service', autospec=True)
class TestRetroIssueView:
    def test_post_retro_not_found(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroIssueView()
        validators.assert_function_returns_retrospective_does_not_exist(object_under_test.post,
                                                                        mock_service_function_validation)

    def test_post_api_mismatch(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroIssueView()
        validators.assert_function_returns_api_mismatch(object_under_test.post, mock_service_function_validation,
                                                        retro.create_mock_retro())

    def test_post_user_not_valid(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroIssueView()
        validators.assert_function_returns_user_not_valid(object_under_test.post, mock_service_function_validation,
                                                          mock_token, retro.create_mock_retro())

    def test_post_retro_step_not_valid(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroIssueView()
        mock_retro = retro.create_mock_retro(current_step=RetroStep.VOTING.value)
        validators.assert_function_returns_retro_not_on_step(object_under_test.post, mock_service_function_validation,
                                                             mock_token, mock_retro,
                                                             views.no_create_issue_retro_wrong_step.format(
                                                                 mock_retro.current_step))

    def test_post_new_issue_success(self, mock_service_function_validation, mock_service_view, mock_token):
        request_body = {
            'title': 'More timely PR reviews',
            'section': 'Needs Improvement'
        }
        mock_service_function_validation.return_value.get_retro.return_value = retro.create_mock_retro()
        mock_token.token_is_valid.return_value = True
        mock_issue_id = 'new_issue_id'
        mock_service_view.add_new_issue.return_value = mock_issue_id

        object_under_test = RetroIssueView()
        response = object_under_test.post(request.create_mock_request(request_body, retro_id='whatever'))

        assert response.status_code == 201
        assert response.headers[validators.content_type] == content_type_application_json
        assert json.loads(response.body) == {'id': mock_issue_id}

    def test_put_retro_not_found(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroIssueView()
        validators.assert_function_returns_retrospective_does_not_exist(object_under_test.put,
                                                                        mock_service_function_validation)

    def test_put_api_mismatch(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroIssueView()
        validators.assert_function_returns_api_mismatch(object_under_test.put, mock_service_function_validation,
                                                        retro.create_mock_retro())

    def test_put_user_not_valid(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroIssueView()
        validators.assert_function_returns_user_not_valid(object_under_test.put, mock_service_function_validation,
                                                          mock_token, retro.create_mock_retro())

    def test_put_not_voting_step(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroIssueView()
        mock_retro = retro.create_mock_retro(current_step=RetroStep.ADDING_ISSUES.value)
        validators.assert_function_returns_retro_not_on_step(object_under_test.put, mock_service_function_validation,
                                                             mock_token, mock_retro,
                                                             views.no_vote_issue_retro_wrong_step.format(
                                                                 mock_retro.current_step))

    def test_put_issue_doesnt_exist(self, mock_service_function_validation, mock_service_view, mock_token):
        issue_id = 'non-existing_id'
        mock_service_function_validation.return_value.get_retro.return_value = retro.create_mock_retro(current_step=RetroStep.VOTING.value,
                                                                                          issues=[retro.create_mock_issue(
                                                                                     id='some_other_id')])
        mock_token.token_is_valid.return_value = True

        object_under_test = RetroIssueView()
        response = object_under_test.put(request.create_mock_request(retro_id='whatever', issue_id=issue_id))

        validators.assert_issue_not_found(response, issue_id)

    def test_put_issue_vote_success(self, mock_service_function_validation, mock_service_view, mock_token):
        request_body = {
            'vote': True,
        }
        mock_issue_id = 'some_issue_id'
        mock_service_function_validation.return_value.get_retro.return_value = retro.create_mock_retro(
            current_step=RetroStep.VOTING.value, issues=[retro.create_mock_issue(id=mock_issue_id)])
        mock_token.token_is_valid.return_value = True

        object_under_test = RetroIssueView()
        response = object_under_test.put(
            request.create_mock_request(request_body, retro_id='whatever', issue_id=mock_issue_id))

        assert mock_service_view.vote_for_issue.called is True
        assert 200 == response.status_code
        assert views.content_type_text_plain == response.headers[validators.content_type]
        assert '' == response.body

    def test_put_issue_unvote_success(self, mock_service_function_validation, mock_service_view, mock_token):
        request_body = {
            'vote': False,
        }
        mock_issue_id = 'some_issue_id'
        mock_service_function_validation.return_value.get_retro.return_value = retro.create_mock_retro(current_step=RetroStep.VOTING.value,
                                                                                          issues=[retro.create_mock_issue(
                                                                                     id=mock_issue_id)])
        mock_token.token_is_valid.return_value = True

        object_under_test = RetroIssueView()
        response = object_under_test.put(
            request.create_mock_request(request_body, retro_id='whatever', issue_id=mock_issue_id))

        assert mock_service_view.unvote_for_issue.called is True
        assert 200 == response.status_code
        assert views.content_type_text_plain == response.headers[validators.content_type]
        assert '' == response.body

    def test_delete_retro_not_found(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroIssueView()
        validators.assert_function_returns_retrospective_does_not_exist(object_under_test.delete,
                                                                        mock_service_function_validation)

    def test_delete_api_mismatch(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroIssueView()
        validators.assert_function_returns_api_mismatch(object_under_test.delete, mock_service_function_validation,
                                                        retro.create_mock_retro())

    def test_delete_user_not_valid(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroIssueView()
        validators.assert_function_returns_user_not_valid(object_under_test.delete, mock_service_function_validation,
                                                          mock_token, retro.create_mock_retro())

    def test_delete_retro_step_not_valid(self, mock_service_function_validation, mock_service_view, mock_token):
        object_under_test = RetroIssueView()
        mock_retro = retro.create_mock_retro(current_step=RetroStep.VOTING.value)
        validators.assert_function_returns_retro_not_on_step(object_under_test.delete, mock_service_function_validation,
                                                             mock_token, mock_retro,
                                                             views.no_delete_issue_retro_wrong_step.format(
                                                                 mock_retro.current_step))

    def test_delete_issue_doesnt_exist(self, mock_service_function_validation, mock_service_view, mock_token):
        issue_id = 'non-existing_id'
        mock_service_function_validation.return_value.get_retro.return_value = retro.create_mock_retro(
            current_step=RetroStep.ADDING_ISSUES.value, issues=[retro.create_mock_issue(id='some_other_id')])
        mock_token.token_is_valid.return_value = True

        object_under_test = RetroIssueView()
        response = object_under_test.delete(request.create_mock_request(retro_id='whatever', issue_id=issue_id))

        validators.assert_issue_not_found(response, issue_id)

    def test_delete_issue_not_owned_by_user(self, mock_service_function_validation, mock_service_view, mock_token):
        issue_id = 'issue_id'
        mock_service_function_validation.return_value.get_retro.return_value = retro.create_mock_retro(
            current_step=RetroStep.ADDING_ISSUES.value, issues=[retro.create_mock_issue(id=issue_id)])
        mock_token.token_is_valid.return_value = True
        mock_token.issue_owned_by_participant.return_value = False

        object_under_test = RetroIssueView()
        response = object_under_test.delete(request.create_mock_request(retro_id='whatever', issue_id=issue_id))

        validators.assert_user_not_owner_of_issue(response, issue_id)

    def test_delete_success(self, mock_service_function_validation, mock_service_view, mock_token):
        issue_id = 'issue_id'
        mock_service_function_validation.return_value.get_retro.return_value = retro.create_mock_retro(
            current_step=RetroStep.ADDING_ISSUES.value, issues=[retro.create_mock_issue(id=issue_id)])
        mock_token.token_is_valid.return_value = True
        mock_token.issue_owned_by_participant.return_value = True

        object_under_test = RetroIssueView()
        response = object_under_test.delete(request.create_mock_request(retro_id='whatever', issue_id=issue_id))

        assert 204 == response.status_code
        assert views.content_type_text_plain == response.headers[validators.content_type]
        assert '' == response.body
