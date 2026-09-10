from __future__ import annotations

import os

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, APITimeoutError
from tests.respx2 import MockRouter

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


@pytest.mark.respx2(base_url=base_url)
def test_respx2_preserves_native_sync_family_and_request_content(client: OpenAI, respx2_mock: MockRouter) -> None:
    def mirror(request: httpx2.Request) -> httpx2.Response:
        assert request.url.path == "/upload"
        assert request.headers["x-test"] == "sync"
        return httpx2.Response(200, content=request.content)

    respx2_mock.post("/upload").mock(side_effect=mirror)

    response = client.post(
        "/upload", content=b"sync body", options={"headers": {"x-test": "sync"}}, cast_to=httpx2.Response
    )

    assert isinstance(response, httpx2.Response)
    assert isinstance(response.request, httpx2.Request)
    assert response.content == b"sync body"
    assert len(respx2_mock.calls) == 1


@pytest.mark.respx2(base_url=base_url)
async def test_respx2_preserves_native_async_family_and_request_content(
    async_client: AsyncOpenAI, respx2_mock: MockRouter
) -> None:
    async def mirror(request: httpx2.Request) -> httpx2.Response:
        assert request.url.path == "/upload"
        assert request.headers["x-test"] == "async"
        return httpx2.Response(200, content=await request.aread())

    respx2_mock.post("/upload").mock(side_effect=mirror)

    response = await async_client.post(
        "/upload", content=b"async body", options={"headers": {"x-test": "async"}}, cast_to=httpx2.Response
    )

    assert isinstance(response, httpx2.Response)
    assert isinstance(response.request, httpx2.Request)
    assert response.content == b"async body"
    assert len(respx2_mock.calls) == 1


@pytest.mark.respx2(base_url=base_url)
def test_respx2_maps_timeout_to_native_family(client: OpenAI, respx2_mock: MockRouter) -> None:
    respx2_mock.get("/models").mock(side_effect=httpx2.ReadTimeout("mock timeout"))

    with pytest.raises(APITimeoutError) as exc_info:
        client.with_options(max_retries=0).models.list()

    assert isinstance(exc_info.value.__cause__, httpx2.ReadTimeout)
