from __future__ import annotations

import os

import httpx
import pytest
from respx import MockRouter

from openai import OpenAI, AsyncOpenAI, APITimeoutError

httpx2 = pytest.importorskip("httpx2")
base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
pytestmark = pytest.mark.skipif(
    os.environ.get("OPENAI_TEST_HTTP_CLIENT") != "httpx2", reason="requires the HTTPX2 test lane"
)


@pytest.mark.respx(base_url=base_url)
def test_respx_bridge_preserves_native_sync_family_and_request_content(client: OpenAI, respx_mock: MockRouter) -> None:
    def mirror(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/upload"
        assert request.headers["x-test"] == "sync"
        return httpx.Response(200, content=request.content)

    respx_mock.post("/upload").mock(side_effect=mirror)

    response = client.post(
        "/upload", content=b"sync body", options={"headers": {"x-test": "sync"}}, cast_to=httpx2.Response
    )

    assert isinstance(response, httpx2.Response)
    assert isinstance(response.request, httpx2.Request)
    assert response.content == b"sync body"
    assert len(respx_mock.calls) == 1


@pytest.mark.respx(base_url=base_url)
async def test_respx_bridge_preserves_native_async_family_and_request_content(
    async_client: AsyncOpenAI, respx_mock: MockRouter
) -> None:
    async def mirror(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/upload"
        assert request.headers["x-test"] == "async"
        return httpx.Response(200, content=await request.aread())

    respx_mock.post("/upload").mock(side_effect=mirror)

    response = await async_client.post(
        "/upload", content=b"async body", options={"headers": {"x-test": "async"}}, cast_to=httpx2.Response
    )

    assert isinstance(response, httpx2.Response)
    assert isinstance(response.request, httpx2.Request)
    assert response.content == b"async body"
    assert len(respx_mock.calls) == 1


@pytest.mark.respx(base_url=base_url)
def test_respx_bridge_maps_timeout_to_native_family(client: OpenAI, respx_mock: MockRouter) -> None:
    respx_mock.get("/models").mock(side_effect=httpx.ReadTimeout("mock timeout"))

    with pytest.raises(APITimeoutError) as exc_info:
        client.with_options(max_retries=0).models.list()

    assert isinstance(exc_info.value.__cause__, httpx2.ReadTimeout)
