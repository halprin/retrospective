from django.http import HttpResponse, JsonResponse
from django.views import View
import json
from backend.api import service, token
from backend.api.models import RetroStep
from backend.api.validation import retrospective_exists, user_is_admin, user_is_valid, retro_on_step


charset_utf8 = 'UTF-8'
content_type_text_plain = 'text/plain'
no_create_issue_retro_wrong_step = 'Cannot create an issue because the retrospective is on step {}'
no_vote_issue_retro_wrong_step = 'Cannot vote for an issue because the retrospective is on step {}'
no_delete_issue_retro_wrong_step = 'Cannot delete an issue because the retrospective is on step {}'


class RetroView(View):
    def post(self, request, *args, **kwargs):
        request_body = json.loads(request.body)
        retro_name = request_body['retroName']
        admin_name = request_body['adminName']

        new_retro = service.create_retro(retro_name, admin_name)

        response_body = {
            'retroId': new_retro.id,
            'token': new_retro.participants[0].token
        }

        return JsonResponse(response_body, status=201, charset=charset_utf8)

    @retrospective_exists
    @user_is_admin
    def put(self, request, retro=None, *args, **kwargs):
        request_body = json.loads(request.body)
        direction = request_body['direction']

        new_step = None
        try:
            new_step = service.move_retro(retro, direction)
        except ValueError as exception:
            return HttpResponse(str(exception), status=422, content_type=content_type_text_plain, charset=charset_utf8)

        response_body = {
            'newStep': new_step
        }

        return JsonResponse(response_body, status=200, charset=charset_utf8)

    @retrospective_exists
    @user_is_valid
    def get(self, request, retro=None, *args, **kwargs):
        user_token = token.get_token_from_request(request)
        response_body = service.sanitize_retro_for_user_and_step(retro, user_token)

        return JsonResponse(response_body, status=200, charset=charset_utf8)


class RetroUserView(View):
    @retrospective_exists
    def post(self, request, retro=None, *args, **kwargs):
        request_body = json.loads(request.body)
        participant_name = request_body['name']

        participant_token = service.add_participant(participant_name, retro)

        response_body = {
            'token': participant_token
        }

        return JsonResponse(response_body, status=201, charset=charset_utf8)

    @retrospective_exists
    @user_is_valid
    def put(self, request, retro=None, *args, **kwargs):
        user_token = token.get_token_from_request(request)

        request_body = json.loads(request.body)
        is_ready = request_body['ready']

        service.mark_user_as_ready(user_token, is_ready, retro)

        return HttpResponse('', status=200, content_type=content_type_text_plain, charset=charset_utf8)


class RetroIssueView(View):
    @retrospective_exists
    @user_is_valid
    @retro_on_step(RetroStep.ADDING_ISSUES, no_create_issue_retro_wrong_step)
    def post(self, request, retro=None, *args, **kwargs):
        user_token = token.get_token_from_request(request)

        request_body = json.loads(request.body)
        issue_title = request_body['title']
        issue_section = request_body['section']

        new_issue_id = service.add_new_issue(issue_title, issue_section, user_token, retro)

        response_body = {
            'id': new_issue_id
        }

        return JsonResponse(response_body, status=201, charset=charset_utf8)

    @retrospective_exists
    @user_is_valid
    @retro_on_step(RetroStep.VOTING, no_vote_issue_retro_wrong_step)
    def put(self, request, retro=None, issue_id=None, *args, **kwargs):
        issue_id_str = str(issue_id)
        user_token = token.get_token_from_request(request)

        service.vote_for_issue(issue_id_str, user_token, retro)

        return HttpResponse('', status=200, content_type=content_type_text_plain, charset=charset_utf8)

    def delete(self, request, retro_id=None, issue_id=None, *args, **kwargs):
        retro_id_str = str(retro_id)
        issue_id_str = str(issue_id)

        retro = None
        try:
            retro = service.get_retro(retro_id_str)
        except Retrospective.DoesNotExist:
            return HttpResponse(retro_not_found.format(retro_id_str), status=404, content_type=content_type_text_plain,
                                charset=charset_utf8)

        user_token = token.get_token_from_request(request)
        if not token.token_is_valid(user_token, retro):
            return HttpResponse(user_not_valid, status=401, content_type=content_type_text_plain, charset=charset_utf8)

        if not token.token_is_valid(user_token, retro):
            return HttpResponse(user_not_valid, status=401, content_type=content_type_text_plain, charset=charset_utf8)

        if RetroStep(retro.current_step) != RetroStep.ADDING_ISSUES:
            return HttpResponse(no_delete_issue_retro_wrong_step.format(retro.current_step), status=422,
                                content_type=content_type_text_plain, charset=charset_utf8)


class HealthView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('', status=200, content_type=content_type_text_plain, charset=charset_utf8)
