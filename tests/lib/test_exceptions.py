from __future__ import annotations

import httpx

from openai._exceptions import BadRequestError


def _make_error(body: dict[str, object]) -> BadRequestError:
    request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    response = httpx.Response(400, request=request)
    return BadRequestError(message="test error", response=response, body=body)


def test_integer_error_code_is_preserved() -> None:
    # The OpenAI API can return integer error codes (e.g. 1006). Constructing
    # the error from such a body must keep the raw int: Pydantic v1 union
    # coercion would otherwise stringify it to "1006".
    err = _make_error({"message": "test error", "code": 123})
    assert err.code == 123
    assert isinstance(err.code, int)


def test_string_error_code_is_preserved() -> None:
    # String codes (the common case) must keep working unchanged.
    err = _make_error({"message": "test error", "code": "rate_limit_exceeded"})
    assert err.code == "rate_limit_exceeded"


def test_missing_or_invalid_error_code_is_none() -> None:
    assert _make_error({"message": "test error"}).code is None
    assert _make_error({"message": "test error", "code": {"nested": True}}).code is None
