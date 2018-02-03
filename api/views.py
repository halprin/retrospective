from django.http import HttpResponse, JsonResponse
from django.views import View
import json
from api import service, token
from api.models import Retrospective, RetroStep


charset_utf8 = 'UTF-8'
content_type_text_plain = 'text/plain'
retro_not_found = 'Retro {} not found'
user_not_admin = 'User is not valid or not an admin'
user_not_valid = 'User is not valid'


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

    def put(self, request, retro_id=None, *args, **kwargs):
        retro_id_str = str(retro_id)

        retro = None
        try:
            retro = service.get_retro(retro_id_str)
        except Retrospective.DoesNotExist:
            return HttpResponse(retro_not_found.format(retro_id_str), status=404, content_type=content_type_text_plain,
                                charset=charset_utf8)

        if not token.token_is_admin(token.get_token_from_request(request), retro):
            return HttpResponse(user_not_admin, status=401, content_type=content_type_text_plain, charset=charset_utf8)

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

    def get(self, request, retro_id=None, *args, **kwargs):
        retro_id_str = str(retro_id)

        retro = None
        try:
            retro = service.get_retro(retro_id_str)
        except Retrospective.DoesNotExist:
            return HttpResponse(retro_not_found.format(retro_id_str), status=404, content_type=content_type_text_plain,
                                charset=charset_utf8)

        user_token = token.get_token_from_request(request)
        if not token.token_is_valid(user_token, retro):
            return HttpResponse(user_not_valid, status=401, content_type=content_type_text_plain, charset=charset_utf8)

        response_body = service.sanitize_retro_for_user_and_step(retro, user_token)

        return JsonResponse(response_body, status=200, charset=charset_utf8)


class RetroUserView(View):
    def post(self, request, retro_id=None, *args, **kwargs):
        retro_id_str = str(retro_id)

        retro = None
        try:
            retro = service.get_retro(retro_id_str)
        except Retrospective.DoesNotExist:
            return HttpResponse(retro_not_found.format(retro_id_str), status=404, content_type=content_type_text_plain,
                                charset=charset_utf8)

        request_body = json.loads(request.body)
        participant_name = request_body['name']

        participant_token = service.add_participant(participant_name, retro)

        response_body = {
            'token': participant_token
        }

        return JsonResponse(response_body, status=201, charset=charset_utf8)

    def put(self, request, retro_id=None, *args, **kwargs):
        retro_id_str = str(retro_id)

        retro = None
        try:
            retro = service.get_retro(retro_id_str)
        except Retrospective.DoesNotExist:
            return HttpResponse(retro_not_found.format(retro_id_str), status=404, content_type=content_type_text_plain,
                                charset=charset_utf8)

        user_token = token.get_token_from_request(request)
        if not token.token_is_valid(user_token, retro):
            return HttpResponse(user_not_valid, status=401, content_type=content_type_text_plain, charset=charset_utf8)

        request_body = json.loads(request.body)
        is_ready = request_body['ready']

        service.mark_user_as_ready(user_token, is_ready, retro)

        return HttpResponse('', status=200, content_type=content_type_text_plain, charset=charset_utf8)


class RetroIssueView(View):
    def post(self, request, retro_id=None, *args, **kwargs):
        retro_id_str = str(retro_id)

        retro = None
        try:
            retro = service.get_retro(retro_id_str)
        except Retrospective.DoesNotExist:
            return HttpResponse(retro_not_found.format(retro_id_str), status=404, content_type=content_type_text_plain,
                                charset=charset_utf8)

        user_token = token.get_token_from_request(request)
        if not token.token_is_valid(user_token, retro):
            return HttpResponse(status=401)

        if RetroStep(retro.current_step) != RetroStep.ADDING_ISSUES:
            return HttpResponse('Cannot create an issue since the retrospective is on step {}'.format(retro.current_step), status=422)

        request_body = json.loads(request.body)
        issue_title = request_body['title']
        issue_section = request_body['section']

        new_issue_id = service.add_new_issue(issue_title, issue_section, user_token, retro)

        response_body = {
            'id': new_issue_id
        }

        return JsonResponse(response_body, status=201)

    def put(self, request, retro_id=None, issue_id=None, *args, **kwargs):
        return HttpResponse('Hello World', status=200)
