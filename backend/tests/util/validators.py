from backend.api import validation


content_type = 'Content-Type'


def assert_retro_not_found(response, retro_id):
    assert 404 == response.status_code
    assert validation.content_type_text_plain == response[content_type]
    assert validation.charset_utf8 == response.charset
    assert validation.retro_not_found.format(retro_id) == response.content.decode()


def assert_user_not_admin(response):
    assert 401 == response.status_code
    assert validation.content_type_text_plain == response[content_type]
    assert validation.charset_utf8 == response.charset
    assert validation.user_not_admin == response.content.decode()


def assert_user_not_valid(response):
    assert 401 == response.status_code
    assert validation.content_type_text_plain == response[content_type]
    assert validation.charset_utf8 == response.charset
    assert validation.user_not_valid == response.content.decode()


def assert_retro_not_on_step(response, expected_error_message):
    assert 422 == response.status_code
    assert validation.content_type_text_plain == response[content_type]
    assert validation.charset_utf8 == response.charset
    assert expected_error_message == response.content.decode()
