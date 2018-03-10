import uuid


def generate_token():
    return str(uuid.uuid4())


def get_token_from_request(request):
    return request.META.get('HTTP_AUTHORIZATION', '')[len('Bearer '):]


def get_participant(token, retro):
    return _find_participant(lambda participant: participant.token == token, retro)


def token_is_valid(token, retro):
    return get_participant(token, retro) is not None


def token_is_admin(token, retro):
    return _find_participant(lambda participant: participant.admin is True and participant.token == token,
                             retro) is not None


def _find_participant(func, retro):
    participant_iterator = filter(func, retro.participants)
    try:
        return participant_iterator.__next__()
    except StopIteration:
        return None
