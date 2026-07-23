from __future__ import annotations

import os
from typing import Any, NoReturn

import httpx
import pytest
from respx import MockRouter

from openai import DefaultHttpx2Client, DefaultAsyncHttpx2Client


def httpx2_enabled() -> bool:
    return os.environ.get("OPENAI_TEST_HTTP_CLIENT") == "httpx2"


def sync_http_client(**kwargs: Any) -> httpx.Client:
    if httpx2_enabled():
        return DefaultHttpx2Client(**kwargs)
    return httpx.Client(**kwargs)


def async_http_client(**kwargs: Any) -> httpx.AsyncClient:
    if httpx2_enabled():
        return DefaultAsyncHttpx2Client(**kwargs)
    return httpx.AsyncClient(**kwargs)


def enable_httpx2_respx(
    router: MockRouter, monkeypatch: pytest.MonkeyPatch, *, replace_sdk_defaults: bool = True
) -> None:
    httpx2 = pytest.importorskip("httpx2")

    # RESPX deliberately only understands HTTPX objects. Keep the SDK side native and
    # translate at this single test-only boundary so existing routes, callbacks, and
    # call assertions can be exercised against HTTPX2 without copied test cases.
    def httpx_request(native_request: Any, *, content: bytes) -> httpx.Request:
        return httpx.Request(
            native_request.method,
            str(native_request.url),
            headers=list(native_request.headers.multi_items()),
            content=content,
            extensions=dict(native_request.extensions),
        )

    def httpx2_response(response: httpx.Response, *, native_request: Any, content: bytes) -> Any:
        return httpx2.Response(
            response.status_code,
            headers=list(response.headers.multi_items()),
            # Supplying a stream keeps streaming-response tests meaningful: the native
            # response stays open until the SDK consumes or closes it.
            stream=httpx2.ByteStream(content),
            request=native_request,
            extensions=dict(response.extensions),
        )

    def raise_native_request_error(exc: httpx.RequestError, native_request: Any) -> NoReturn:
        native_error = getattr(httpx2, type(exc).__name__, httpx2.RequestError)
        raise native_error(str(exc), request=native_request) from exc

    def handler(native_request: Any) -> Any:
        try:
            response = router.handler(httpx_request(native_request, content=native_request.read()))
        except httpx.RequestError as exc:
            raise_native_request_error(exc, native_request)
        return httpx2_response(response, native_request=native_request, content=response.read())

    async def async_handler(native_request: Any) -> Any:
        try:
            response = await router.async_handler(httpx_request(native_request, content=await native_request.aread()))
        except httpx.RequestError as exc:
            raise_native_request_error(exc, native_request)
        return httpx2_response(response, native_request=native_request, content=await response.aread())

    # Match RESPX's own patch point. This also catches clients created inside a test,
    # while leaving every non-RESPX test on its ordinary transport.
    def sync_transport(*_args: Any) -> Any:
        return httpx2.MockTransport(handler)

    def async_transport(*_args: Any) -> Any:
        return httpx2.MockTransport(async_handler)

    monkeypatch.setattr(httpx2.Client, "_transport_for_url", sync_transport)
    monkeypatch.setattr(httpx2.AsyncClient, "_transport_for_url", async_transport)

    if replace_sdk_defaults:
        import openai._base_client as base_client

        # Clients constructed inside a RESPX test should exercise the same native
        # path as the shared fixtures; the base-compatibility tests opt out.
        monkeypatch.setattr(base_client, "SyncHttpxClientWrapper", DefaultHttpx2Client)
        monkeypatch.setattr(base_client, "AsyncHttpxClientWrapper", DefaultAsyncHttpx2Client)
