import json
import logging

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, InternalServerError
from tests.respx2 import MockRouter

from .conftest import base_url


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize(
    "body,expected_message",
    [
        pytest.param(
            '{"error": {"message": "Upstream failure", "details": "extra-response-data"},'
            ' "details": "extra-response-data"}',
            "Error code: 500 - Upstream failure",
            id="nested-message",
        ),
        pytest.param("<html>extra-response-data</html>", "Error code: 500", id="non-json"),
    ],
)
@pytest.mark.respx2(base_url=base_url)
async def test_status_error_message(
    sync: bool,
    body: str,
    expected_message: str,
    client: OpenAI,
    async_client: AsyncOpenAI,
    respx2_mock: MockRouter,
    caplog: pytest.LogCaptureFixture,
) -> None:
    respx2_mock.get("/example").mock(return_value=httpx2.Response(500, text=body))

    with pytest.raises(InternalServerError) as exc_info:
        if sync:
            client.with_options(max_retries=0).get("/example", cast_to=object)
        else:
            await async_client.with_options(max_retries=0).get("/example", cast_to=object)

    error = exc_info.value
    assert str(error) == expected_message
    assert error.response.text == body
    try:
        parsed = json.loads(body)
    except ValueError:
        assert error.body == body
    else:
        assert error.body == parsed["error"]

    logging.getLogger(__name__).error("Request failed", exc_info=(type(error), error, error.__traceback__))
    assert expected_message in caplog.text
    assert "extra-response-data" not in caplog.text
