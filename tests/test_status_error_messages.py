import json
import logging
import traceback

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
            json.dumps(
                {
                    "error": {
                        "message": "Upstream failure",
                        "code": "server_error",
                        "type": "example_error",
                        "param": "input",
                        "details": "extra-response-data",
                    },
                    "details": "extra-response-data",
                }
            ),
            "Error code: 500 - Upstream failure",
            id="nested-message",
        ),
        pytest.param(
            '{"message": "Upstream failure", "details": "extra-response-data"}',
            "Error code: 500 - Upstream failure",
            id="top-level-message",
        ),
        pytest.param(
            '{"error": {"message": {"details": "extra-response-data"}}}',
            "Error code: 500",
            id="non-string-message",
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
    respx2_mock.get("/example").mock(
        return_value=httpx2.Response(
            500, text=body, headers={"x-request-id": "req_example", "set-cookie": "example-cookie"}
        )
    )

    with pytest.raises(InternalServerError) as exc_info:
        if sync:
            client.with_options(max_retries=0).get("/example", cast_to=object)
        else:
            await async_client.with_options(max_retries=0).get("/example", cast_to=object)

    error = exc_info.value
    assert str(error) == expected_message
    assert error.status_code == 500
    assert error.request_id == "req_example"
    assert error.response.text == body
    assert error.response.headers["set-cookie"] == "example-cookie"
    try:
        parsed = json.loads(body)
    except ValueError:
        assert error.body == body
    else:
        expected_body = parsed.get("error", parsed)
        assert error.body == expected_body
        if "code" in expected_body:
            assert (error.code, error.type, error.param) == ("server_error", "example_error", "input")

    logging.getLogger(__name__).error("Request failed", exc_info=(type(error), error, error.__traceback__))
    for rendered in (repr(error), "".join(traceback.format_exception(error)), caplog.text):
        assert "extra-response-data" not in rendered
        assert "example-cookie" not in rendered
