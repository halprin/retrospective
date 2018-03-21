from unittest.mock import patch
from backend.api import validation
from backend.api.models import Retrospective
from backend.tests.util import retro


content_type = 'Content-Type'


def original_function(*args, **kwargs):
    return {
        'args': args,
        'kwargs': kwargs
    }


@patch('backend.api.validation.service', autospec=True)
def test_retrospective_exists_negative(mock_service):
    mock_service.get_retro.side_effect = Retrospective.DoesNotExist

    retro_id = 'non-existent_retro_id'
    object_under_test = validation.retrospective_exists(original_function)
    response = object_under_test(retro_id=retro_id)

    assert 404 == response.status_code
    assert validation.content_type_text_plain == response[content_type]
    assert validation.charset_utf8 == response.charset
    assert validation.retro_not_found.format(retro_id) == response.content.decode()


@patch('backend.api.validation.service', autospec=True)
def test_retrospective_exists_positive(mock_service):
    mock_retro = retro.create_mock_retro()
    mock_service.get_retro.return_value = mock_retro

    passed_in_retro_id = 'some_retro_id'
    object_under_test = validation.retrospective_exists(original_function)
    passed_args = object_under_test(retro_id=passed_in_retro_id)

    assert mock_retro == passed_args['args'][0]
    assert passed_in_retro_id == passed_args['kwargs']['retro_id']
