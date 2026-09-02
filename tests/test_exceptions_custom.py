import httpx
import pytest
import openai
from openai import OpenAI, BadRequestError
from respx import MockRouter

base_url = "https://api.openai.com/v1"

@pytest.mark.respx(base_url=base_url)
def test_error_code_integer_parsing(respx_mock: MockRouter) -> None:
    respx_mock.post("/chat/completions").mock(
        return_value=httpx.Response(
            400,
            json={
                "error": {
                    "message": "The request is invalid.",
                    "type": "invalid_request_error",
                    "code": 400,
                    "param": "model"
                }
            }
        )
    )

    client = OpenAI(base_url=base_url, api_key="test-api-key")
    
    with pytest.raises(BadRequestError) as exc_info:
        client.chat.completions.create(messages=[{"role": "user", "content": "hello"}], model="gpt-4")

    assert exc_info.value.status_code == 400
    assert exc_info.value.code == 400
    assert "The request is invalid." in exc_info.value.message
    assert exc_info.value.param == "model"
