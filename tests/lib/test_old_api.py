import pytest

import openai
from openai.lib._old_api import APIRemovedInV1


def test_basic_attribute_access_works() -> None:
    for attr in dir(openai):
        dir(getattr(openai, attr))


def test_helpful_error_is_raised() -> None:
    with pytest.raises(APIRemovedInV1):
        openai.Completion.create()  # type: ignore

    with pytest.raises(APIRemovedInV1):
        openai.ChatCompletion.create()  # type: ignore
