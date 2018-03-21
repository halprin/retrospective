from functools import wraps
from django.http import HttpResponse
from backend.api import service
from backend.api.models import Retrospective


charset_utf8 = 'UTF-8'
content_type_text_plain = 'text/plain'
retro_not_found = 'Retro {} not found'


def retrospective_exists(original_function):
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        retro_id = kwargs['retro_id']
        retro_id_str = str(retro_id)

        retro = None
        try:
            retro = service.get_retro(retro_id_str)
        except Retrospective.DoesNotExist:
            return HttpResponse(retro_not_found.format(retro_id_str), status=404, content_type=content_type_text_plain,
                                charset=charset_utf8)

        return original_function(*args, retro, **kwargs)

    return wrapper
