from __future__ import annotations

from unittest import mock

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, APIStatusError


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize(
    "status,headers,delay",
    [
        (429, {"retry-after": "1e999"}, None),
        (503, {"retry-after": "9" * 400}, None),
        (429, {"retry-after-ms": "1e999"}, None),
        (503, {"retry-after-ms": "9" * 400}, None),
        (401, {"retry-after": "1e999", "x-should-retry": "true"}, None),
        (429, {"retry-after": "inf"}, 0.5),
        (503, {"retry-after": " +Infinity "}, 0.5),
        (429, {"retry-after": "NaN"}, 0.5),
        (429, {"retry-after": "-1e999"}, 0.5),
        (429, {"retry-after-ms": "inf", "retry-after": "90"}, 0.5),
        (429, {"retry-after": "1e2"}, 100.0),
        (503, {"retry-after-ms": "1e5"}, 100.0),
    ],
)
async def test_retry_after_numeric_overflow(
    async_mode: bool, status: int, headers: dict[str, str], delay: float | None
) -> None:
    attempts = 0
    body = {"message": "Synthetic retry error", "type": "synthetic_error", "code": "synthetic_code"}

    def handle(request: httpx2.Request) -> httpx2.Response:
        nonlocal attempts
        attempts += 1
        assert request.url.path == "/models/test"
        return httpx2.Response(status, headers={**headers, "x-request-id": "synthetic-id"}, json={"error": body})

    with mock.patch("time.sleep") as sync_sleep, mock.patch("anyio.sleep") as async_sleep:
        with mock.patch("openai._base_client.random", return_value=0), pytest.raises(APIStatusError) as exc:
            if async_mode:
                async with AsyncOpenAI(
                    api_key="synthetic-key",
                    base_url="https://retry.test",
                    max_retries=1,
                    http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handle), trust_env=False),
                ) as async_client:
                    await async_client.models.retrieve("test")
            else:
                with OpenAI(
                    api_key="synthetic-key",
                    base_url="https://retry.test",
                    max_retries=1,
                    http_client=httpx2.Client(transport=httpx2.MockTransport(handle), trust_env=False),
                ) as client:
                    client.models.retrieve("test")

    assert attempts == (1 if delay is None else 2)
    assert (async_sleep if async_mode else sync_sleep).call_args_list == ([] if delay is None else [mock.call(delay)])
    assert exc.value.status_code == status
    assert exc.value.body == body
    assert exc.value.request_id == "synthetic-id"
    assert all(exc.value.response.headers[key] == value for key, value in headers.items())
