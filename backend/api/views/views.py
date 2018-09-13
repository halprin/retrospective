from typing import Union
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.views import View
import json
from backend.api import token
from backend.api.service import Service
from backend.api.models import RetroStep, Retrospective, IssueAttribute
from backend.api.validation import retrospective_exists, user_is_admin, user_is_valid, retro_on_step, issue_exists,\
    issue_owned_by_user, retrospective_api_is_correct
from .generic_views import VersionServiceView


charset_utf8 = 'UTF-8'
content_type_text_plain = 'text/plain'
no_create_issue_retro_wrong_step = 'Cannot create an issue because the retrospective is on step {}'
no_vote_issue_retro_wrong_step = 'Cannot vote for an issue because the retrospective is on step {}'
no_delete_issue_retro_wrong_step = 'Cannot delete an issue because the retrospective is on step {}'


class Version1ServiceView(VersionServiceView):
    @staticmethod
    def service():
        return Service


class RetroView(Version1ServiceView):
    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        request_body: dict = json.loads(request.body)
        retro_name: str = request_body['retroName']
        admin_name: str = request_body['adminName']

        new_retro: Retrospective = self.service().create_retro(retro_name, admin_name)

        response_body: dict = {
            'retroId': new_retro.id,
            'token': new_retro.participants[0].token
        }

        return JsonResponse(response_body, status=201, charset=charset_utf8)

    @retrospective_exists
    @retrospective_api_is_correct
    @user_is_admin
    def put(self, request: HttpRequest, retro: Retrospective = None, *args, **kwargs) -> Union[
            HttpResponse, JsonResponse]:

        request_body = json.loads(request.body)
        direction: str = request_body['direction']

        new_step: str = None
        try:
            new_step = self.service().move_retro(retro, direction)
        except ValueError as exception:
            return HttpResponse(str(exception), status=422, content_type=content_type_text_plain, charset=charset_utf8)

        response_body: dict = {
            'newStep': new_step
        }

        return JsonResponse(response_body, status=200, charset=charset_utf8)

    @retrospective_exists
    @retrospective_api_is_correct
    @user_is_valid
    def get(self, request: HttpRequest, retro: Retrospective=None, *args, **kwargs) -> JsonResponse:
        user_token: str = token.get_token_from_request(request)
        response_body: dict = self.service().sanitize_retro_for_user_and_step(retro, user_token)

        return JsonResponse(response_body, status=200, charset=charset_utf8)


class RetroUserView(Version1ServiceView):
    @retrospective_exists
    @retrospective_api_is_correct
    def post(self, request: HttpRequest, retro: Retrospective=None, *args, **kwargs) -> JsonResponse:
        request_body: dict = json.loads(request.body)
        participant_name: str = request_body['name']

        participant_token: str = Service.add_participant(participant_name, retro)

        response_body: dict = {
            'token': participant_token
        }

        return JsonResponse(response_body, status=201, charset=charset_utf8)

    @retrospective_exists
    @retrospective_api_is_correct
    @user_is_valid
    def put(self, request: HttpRequest, retro: Retrospective=None, *args, **kwargs) -> HttpResponse:
        user_token: str = token.get_token_from_request(request)

        request_body: dict = json.loads(request.body)
        is_ready: bool = request_body['ready']

        self.service().mark_user_as_ready(user_token, is_ready, retro)

        return HttpResponse('', status=200, content_type=content_type_text_plain, charset=charset_utf8)


class RetroIssueView(View):
    @retrospective_exists
    @user_is_valid
    @retro_on_step(RetroStep.ADDING_ISSUES, no_create_issue_retro_wrong_step)
    def post(self, request: HttpRequest, retro: Retrospective=None, *args, **kwargs) -> JsonResponse:
        user_token: str = token.get_token_from_request(request)

        request_body: dict = json.loads(request.body)
        issue_title: str = request_body['title']
        issue_section: str = request_body['section']

        new_issue_id: str = Service.add_new_issue(issue_title, issue_section, user_token, retro)

        response_body: dict = {
            'id': new_issue_id
        }

        return JsonResponse(response_body, status=201, charset=charset_utf8)

    @retrospective_exists
    @user_is_valid
    @retro_on_step(RetroStep.VOTING, no_vote_issue_retro_wrong_step)
    @issue_exists
    def put(self, request: HttpRequest, retro: Retrospective = None, issue: IssueAttribute = None, *args,
            **kwargs) -> HttpResponse:
        user_token: str = token.get_token_from_request(request)

        request_body: dict = json.loads(request.body)
        vote_for: bool = request_body['vote']

        if vote_for:
            Service.vote_for_issue(issue, user_token, retro)
        else:
            Service.unvote_for_issue(issue, user_token, retro)

        return HttpResponse('', status=200, content_type=content_type_text_plain, charset=charset_utf8)

    @retrospective_exists
    @user_is_valid
    @retro_on_step(RetroStep.ADDING_ISSUES, no_delete_issue_retro_wrong_step)
    @issue_exists
    @issue_owned_by_user
    def delete(self, request: HttpRequest, retro: Retrospective = None, issue: IssueAttribute = None, *args,
               **kwargs) -> HttpResponse:
        Service.delete_issue(issue, retro)

        return HttpResponse('', status=204, content_type=content_type_text_plain, charset=charset_utf8)


class HealthView(View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        return HttpResponse('', status=200, content_type=content_type_text_plain, charset=charset_utf8)
