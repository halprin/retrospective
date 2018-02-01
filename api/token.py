import uuid


def generate_token():
    return str(uuid.uuid4())


def get_token_from_request(request):
    return request.META['HTTP_AUTHORIZATION'][len('Bearer '):]


def token_is_valid(token, retro):
    return _find_token(lambda participant: participant.token == token, retro)


def token_is_admin(token, retro):
    return _find_token(lambda participant: participant.admin is True and participant.token == token, retro)


def _find_token(func, retro):
    approved = filter(func, retro.participants)
    try:
        approved.__next__()
        return True
    except StopIteration:
        return False
