from __future__ import annotations

import os
from unittest import mock

import httpx
import pytest
from respx import MockRouter

from openai import OpenAI


base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


def _low_retry_timeout(*_args, **_kwargs) -> float:
    return 0.01


@mock.patch("openai._base_client.BaseClient._calculate_retry_timeout", _low_retry_timeout)
@pytest.mark.respx(base_url=base_url)
def test_retry_after_header_is_respected(respx_mock: MockRouter, client: OpenAI) -> None:
    attempts = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["n"] += 1
        if attempts["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "2"}, json={"err": "rate"})
        return httpx.Response(200, json={"ok": True})

    respx_mock.post("/chat/completions").mock(side_effect=handler)

    client = client.with_options(max_retries=3)

    response = client.chat.completions.with_raw_response.create(
        messages=[{"content": "hi", "role": "user"}],
        model="gpt-4o",
    )

    assert response.retries_taken == 1
    assert int(response.http_request.headers.get("x-stainless-retry-count")) == 1

