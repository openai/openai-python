import httpx

from openai import APIStatusError


def test_integer_error_code_is_coerced_to_string() -> None:
    request = httpx.Request("GET", "https://api.openai.com/v1/models")
    response = httpx.Response(404, request=request)

    error = APIStatusError("Not found", response=response, body={"code": 404})

    assert error.code == "404"
