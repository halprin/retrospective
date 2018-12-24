import json
from typing import Union
from . import views
from .views import RetroView, RetroUserView, RetroIssueView
from .generic.utils import VersionServiceView, Request
from ..serviceV2 import ServiceV2
from ..modelsV2 import RetroStepV2, RetrospectiveV2, IssueAttributeV2, GroupAttribute
from ...api.validation import retrospective_exists, user_is_valid, retro_on_step, issue_exists,\
    retrospective_api_is_correct, group_exists
from ...api import token


no_group_issue_retro_wrong_step = 'Cannot group an issue because the retrospective is on step {}'
no_create_group_retro_wrong_step = 'Cannot create a group because the retrospective is on step {}'
no_vote_group_retro_wrong_step = 'Cannot vote for a group because the retrospective is on step {}'
no_delete_group_retro_wrong_step = 'Cannot delete a group because the retrospective is on step {}'


class Version2ServiceView(VersionServiceView):
    @staticmethod
    def service():
        return ServiceV2


class RetroViewV2(Version2ServiceView, RetroView):
    pass


class RetroUserViewV2(Version2ServiceView, RetroUserView):
    pass


class RetroIssueViewV2(Version2ServiceView, RetroIssueView):
    @retrospective_exists
    @retrospective_api_is_correct
    @user_is_valid
    @issue_exists
    def put(self, request: Request, retro: RetrospectiveV2 = None, issue: IssueAttributeV2 = None):

        request_body: dict = json.loads(request.body)
        vote_for: bool = request_body.get('vote')
        group_id: Union[str, bool] = request_body.get('group')

        if vote_for is not None:
            return super(RetroIssueViewV2, self).put(self, request, retro_id=retro.id, issue_id=issue.id)
        elif group_id is not None:
            return self._group_put(self, issue, retro=retro, group_id=group_id)

    @retro_on_step(RetroStepV2.GROUPING, no_group_issue_retro_wrong_step)
    @group_exists
    def _group_put(self, issue: IssueAttributeV2, retro: RetrospectiveV2 = None, group: GroupAttribute = None):

        if group is not None:
            self.service().group_issue(issue, group, retro)
        else:
            self.service().ungroup_issue(issue, retro)

        return HttpResponse('', status=200, content_type=views.content_type_text_plain, charset=views.charset_utf8)


class RetroGroupViewV2(Version2ServiceView):
    @retrospective_exists
    @retrospective_api_is_correct
    @user_is_valid
    @retro_on_step(RetroStepV2.GROUPING, no_create_group_retro_wrong_step)
    def post(self, request: Request, retro: RetrospectiveV2 = None):
        request_body: dict = json.loads(request.body)
        group_title: str = request_body['title']
        group_section: str = request_body['section']

        new_group_id: str = self.service().add_new_group(group_title, group_section, retro)

        response_body: dict = {
            'id': new_group_id
        }

        return JsonResponse(response_body, status=201, charset=views.charset_utf8)

    @retrospective_exists
    @retrospective_api_is_correct
    @user_is_valid
    @retro_on_step(RetroStepV2.VOTING, no_vote_group_retro_wrong_step)
    @group_exists
    def put(self, request: Request, retro: RetrospectiveV2 = None, group: GroupAttribute = None):

        user_token: str = token.get_token_from_request(request)

        request_body: dict = json.loads(request.body)
        vote_for: bool = request_body['vote']

        if vote_for:
            self.service().vote_for_group(group, user_token, retro)
        else:
            self.service().unvote_for_group(group, user_token, retro)

        return HttpResponse('', status=200, content_type=views.content_type_text_plain, charset=views.charset_utf8)

    @retrospective_exists
    @retrospective_api_is_correct
    @user_is_valid
    @retro_on_step(RetroStepV2.GROUPING, no_delete_group_retro_wrong_step)
    @group_exists
    def delete(self, request: Request, retro: RetrospectiveV2 = None, group: GroupAttribute = None):
        self.service().delete_group(group, retro)

        return HttpResponse('', status=204, content_type=views.content_type_text_plain, charset=views.charset_utf8)