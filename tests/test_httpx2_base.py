from __future__ import annotations

import sys
import asyncio
import warnings
import threading
import subprocess
import importlib.util
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing_extensions import override

import httpx
import respx
import pytest

import openai
from openai import OpenAI, AsyncOpenAI, _httpx2 as httpx2_helpers


def test_base_import_does_not_load_httpx2() -> None:
    subprocess.run([sys.executable, "-c", "import sys; import openai; assert 'httpx2' not in sys.modules"], check=True)


def test_missing_httpx2_extra_is_actionable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(httpx2_helpers.sys, "version_info", (3, 10))

    def missing_httpx2(name: str) -> object:
        raise ImportError(name)

    monkeypatch.setattr(httpx2_helpers.importlib, "import_module", missing_httpx2)

    for helper in (openai.DefaultHttpx2Client, openai.DefaultAsyncHttpx2Client):
        with pytest.raises(RuntimeError, match=r"install the httpx2 extra: pip install 'openai\[httpx2\]'"):
            helper()


def test_python39_httpx2_error_is_actionable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(httpx2_helpers.sys, "version_info", (3, 9))

    for helper in (openai.DefaultHttpx2Client, openai.DefaultAsyncHttpx2Client):
        with pytest.raises(RuntimeError, match=r"HTTPX2 requires Python 3\.10 or later.*openai\[httpx2\]"):
            helper()


@pytest.mark.respx(base_url="https://example.test/v1")
def test_default_httpx_family_and_respx_are_unchanged(respx_mock: respx.MockRouter) -> None:
    route = respx_mock.get("/models").mock(return_value=httpx.Response(200, json={"object": "list", "data": []}))

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        with OpenAI(api_key="test", base_url="https://example.test/v1") as client:
            response = client.models.with_raw_response.list()

    assert route.called
    assert captured == []
    assert isinstance(response.http_response, httpx.Response)
    assert isinstance(response.http_request, httpx.Request)


async def test_existing_httpx_helpers_and_injected_clients_are_unchanged() -> None:
    class SyncHttpxClient(openai.DefaultHttpxClient):
        pass

    class AsyncHttpxClient(openai.DefaultAsyncHttpxClient):
        pass

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"object": "list", "data": []}, request=request)

    with SyncHttpxClient(transport=httpx.MockTransport(handler), trust_env=False) as http_client:
        with OpenAI(api_key="test", base_url="https://example.test/v1", http_client=http_client) as client:
            response = client.models.with_raw_response.list()
            assert isinstance(response.http_response, httpx.Response)

    async with AsyncHttpxClient(transport=httpx.MockTransport(handler), trust_env=False) as http_client:
        async with AsyncOpenAI(api_key="test", base_url="https://example.test/v1", http_client=http_client) as client:
            response = await client.models.with_raw_response.list()
            assert isinstance(response.http_response, httpx.Response)


async def test_existing_aiohttp_adapter_is_unchanged_when_installed() -> None:
    if importlib.util.find_spec("httpx_aiohttp") is None:
        pytest.skip("the aiohttp extra is not installed")

    class ModelsHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"object":"list","data":[]}')

        @override
        def log_message(self, format: str, *_args: object) -> None:  # noqa: A002
            return None

    server = ThreadingHTTPServer(("127.0.0.1", 0), ModelsHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        async with AsyncOpenAI(
            api_key="test",
            base_url=f"http://127.0.0.1:{server.server_port}/v1",
            http_client=openai.DefaultAioHttpClient(),
            max_retries=0,
        ) as client:
            response = await client.models.with_raw_response.list()
    finally:
        await asyncio.to_thread(server.shutdown)
        thread.join()
        server.server_close()

    assert isinstance(response.http_response, httpx.Response)
