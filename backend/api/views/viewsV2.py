from django.http import HttpResponse, HttpRequest
import json
from typing import Union
from . import views
from .views import RetroView, RetroUserView, RetroIssueView
from .generic_views import VersionServiceView
from ..serviceV2 import ServiceV2
from ..modelsV2 import RetroStepV2, RetrospectiveV2, IssueAttributeV2, GroupAttribute
from ...api.validation import retrospective_exists, user_is_valid, retro_on_step, issue_exists,\
    retrospective_api_is_correct, group_exists


no_group_issue_retro_wrong_step = 'Cannot group an issue because the retrospective is on step {}'


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
    def put(self, request: HttpRequest, retro: RetrospectiveV2 = None, issue: IssueAttributeV2 = None, *args,
            **kwargs) -> HttpResponse:

        request_body: dict = json.loads(request.body)
        vote_for: bool = request_body.get('vote')
        group_id: Union[str, bool] = request_body.get('group')

        if vote_for is not None:
            return super(RetroIssueViewV2, self).put(request, retro_id=retro.id, issue_id=issue.id)
        elif group_id is not None:
            return self._group_put(issue, retro=retro, group_id=group_id)

    @retro_on_step(RetroStepV2.GROUPING, no_group_issue_retro_wrong_step)
    @group_exists
    def _group_put(self, issue: IssueAttributeV2, retro: RetrospectiveV2, group: GroupAttribute = None, *args,
                   **kwargs) -> HttpResponse:

        if group is not None:
            self.service().group_issue(issue, group, retro)
        else:
            self.service().ungroup_issue(issue, retro)

        return HttpResponse('', status=200, content_type=views.content_type_text_plain, charset=views.charset_utf8)
