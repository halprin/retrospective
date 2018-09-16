from unittest.mock import patch
from ...api.views import views
from ...api.views import viewsV2
from ...api.views.viewsV2 import RetroIssueViewV2
from ..util import retro, request, validators
from ...api.modelsV2 import RetroStepV2


@patch('backend.api.validation.token', autospec=True)
@patch('backend.api.validation._get_service', autospec=True)
class TestRetroView:
    @patch('backend.api.views.views.RetroIssueView.put', autospec=True)
    def test_put_vote_for_issue(self, mock_super_put, mock_service_function_validation, mock_token):
        request_body = {
            'vote': True,
        }
        mock_issue_id = 'whatever_issue_id'
        mock_service_function_validation.return_value.get_retro.return_value = retro.create_mock_retro(
            current_step=RetroStepV2.VOTING.value, issues=[retro.create_mock_issueV2(id=mock_issue_id)])
        mock_token.token_is_valid.return_value = True

        object_under_test = RetroIssueViewV2()
        object_under_test.put(request.create_mock_request(request_body), retro_id='whatever',
                                         issue_id=mock_issue_id)

        assert mock_super_put.called is True

    @patch('backend.api.views.viewsV2.RetroIssueViewV2._group_put')
    def test_put_group_issue(self, mock_group_put_function, mock_service_function_validation, mock_token):
        request_body = {
            'group': '0f3c2792-fc6c-41d5-a451-bebc3072fcc2',
        }
        mock_issue_id = 'whatever_issue_id'
        mock_service_function_validation.return_value.get_retro.return_value = retro.create_mock_retro(
            current_step=RetroStepV2.VOTING.value, issues=[retro.create_mock_issueV2(id=mock_issue_id)])
        mock_token.token_is_valid.return_value = True

        object_under_test = RetroIssueViewV2()
        object_under_test.put(request.create_mock_request(request_body), retro_id='whatever', issue_id=mock_issue_id)

        assert mock_group_put_function.called is True

    def test__group_put_retro_not_on_step(self, mock_service_function_validation, mock_token):

        mock_group = retro.create_mock_group()
        mock_issue = retro.create_mock_issueV2()
        retro_current_step = RetroStepV2.VOTING.value
        mock_retro = retro.create_mock_retroV2(current_step=retro_current_step, issues=[mock_issue],
                                               groups=[mock_group])

        object_under_test = RetroIssueViewV2()
        response = object_under_test._group_put(mock_issue, retro=mock_retro, group_id=mock_group.id)

        validators.assert_retro_not_on_step(response,
                                            viewsV2.no_group_issue_retro_wrong_step.format(retro_current_step))

    def test__group_put_group_does_not_exist_real_uuid(self, mock_service_function_validation, mock_token):
        non_existing_group_id = '0f3c2792-fc6c-41d5-a451-bebc3072fcc2'
        mock_group = retro.create_mock_group(id='cool_id')
        mock_issue = retro.create_mock_issueV2()
        mock_retro = retro.create_mock_retroV2(current_step=RetroStepV2.GROUPING.value, issues=[mock_issue],
                                               groups=[mock_group])

        object_under_test = RetroIssueViewV2()
        response = object_under_test._group_put(mock_issue, retro=mock_retro, group_id=non_existing_group_id)

        validators.assert_group_not_found(response, non_existing_group_id)

    @patch('backend.api.views.viewsV2.ServiceV2', autospec=True)
    def test__group_put_group_bool_for_group_id(self, mock_service_module, mock_service_function_validation,
                                                mock_token):
        non_existing_group_id = False
        mock_group = retro.create_mock_group(id='cool_id')
        mock_issue = retro.create_mock_issueV2()
        mock_retro = retro.create_mock_retroV2(current_step=RetroStepV2.GROUPING.value, issues=[mock_issue],
                                               groups=[mock_group])

        object_under_test = RetroIssueViewV2()
        response = object_under_test._group_put(mock_issue, retro=mock_retro, group_id=non_existing_group_id)

        assert mock_service_module.ungroup_issue.called is True
        assert 200 == response.status_code
        assert views.content_type_text_plain == response[validators.content_type]
        assert views.charset_utf8 == response.charset
        assert '' == response.content.decode()

    @patch('backend.api.views.viewsV2.ServiceV2', autospec=True)
    def test__group_put_group_real_group_id(self, mock_service_module, mock_service_function_validation, mock_token):
        group_id = '0f3c2792-fc6c-41d5-a451-bebc3072fcc2'
        mock_group = retro.create_mock_group(id=group_id)
        mock_issue = retro.create_mock_issueV2()
        mock_retro = retro.create_mock_retroV2(current_step=RetroStepV2.GROUPING.value, issues=[mock_issue],
                                               groups=[mock_group])

        object_under_test = RetroIssueViewV2()
        response = object_under_test._group_put(mock_issue, retro=mock_retro, group_id=group_id)

        assert mock_service_module.group_issue.called is True
        assert 200 == response.status_code
        assert views.content_type_text_plain == response[validators.content_type]
        assert views.charset_utf8 == response.charset
        assert '' == response.content.decode()
