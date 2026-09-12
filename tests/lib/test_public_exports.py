from openai.lib import type_to_response_format_param
from openai.lib._parsing import type_to_response_format_param as internal_type_to_response_format_param


def test_type_to_response_format_param_is_publicly_exported() -> None:
    assert type_to_response_format_param is internal_type_to_response_format_param
