from __future__ import annotations

import json
from email import policy
from typing import Any, Callable, cast
from email.parser import BytesParser
from email.message import EmailMessage

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, omit
from openai.resources.realtime.calls import Calls, AsyncCalls

OFFER = "v=0\r\ns=Unicode π\r\n"
ANSWER = "v=0\r\ns=answer\r\n"
SETTINGS = {"type": "realtime", "model": "test-model", "future": {"flags": [False, None]}}
MODES = ["multipart", "omitted", "null", "extra-only", "extra-null", "omit-override", "sdp-override"]


def request_args(mode: str) -> dict[str, Any]:
    args: dict[str, Any] = {"sdp": OFFER, "extra_headers": {"content-type": "application/json"}}
    if mode == "multipart":
        args.update(session={"type": "realtime", "model": "overridden"}, extra_body={"session": SETTINGS})
    elif mode == "null":
        args["session"] = None
    elif mode == "extra-only":
        args["extra_body"] = {"session": SETTINGS}
    elif mode == "extra-null":
        args["extra_body"] = {"session": None}
    elif mode == "omit-override":
        args.update(session=SETTINGS, extra_body={"session": omit})
    elif mode == "sdp-override":
        args.update(sdp="superseded", extra_body={"sdp": OFFER, "session": SETTINGS})
    return args


def handler_for(mode: str, calls: list[httpx2.Request]) -> Callable[[httpx2.Request], httpx2.Response]:
    def handler(request: httpx2.Request) -> httpx2.Response:
        calls.append(request)
        assert request.url.path == "/v1/realtime/calls"
        assert request.headers["accept"] == "application/sdp"
        if mode in {"omitted", "omit-override"}:
            assert request.headers["content-type"] == "application/sdp"
            assert request.read() == OFFER.encode()
        else:
            assert request.headers["content-type"].startswith("multipart/form-data; boundary=")
            message = BytesParser(_class=EmailMessage, policy=policy.default).parsebytes(
                ("Content-Type: " + request.headers["content-type"] + "\r\n\r\n").encode() + request.read()
            )
            parts = list(message.iter_parts())
            assert len(parts) == 2
            named = {part.get_param("name", header="content-disposition"): part for part in parts}
            assert named["sdp"].get_content_type() == "application/sdp"
            assert named["sdp"].get_payload(decode=True) == OFFER.encode()
            assert named["session"].get_content_type() == "application/json"
            assert json.loads(cast(bytes, named["session"].get_payload(decode=True))) == (
                None if mode in {"null", "extra-null"} else SETTINGS
            )
            assert all(part.get_filename() is None for part in parts)
        if len(calls) == 1:
            return httpx2.Response(500, json={"error": {"message": "synthetic retry"}}, headers={"retry-after-ms": "1"})
        return httpx2.Response(
            201, content=ANSWER, headers={"content-type": "application/sdp", "location": "/v1/realtime/calls/test-call"}
        )

    return handler


@pytest.mark.parametrize("mode", MODES)
def test_public_create_uses_generated_wire_contract(mode: str) -> None:
    calls: list[httpx2.Request] = []
    with OpenAI(
        api_key="synthetic-test-key",
        base_url="https://example.test/v1",
        max_retries=1,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler_for(mode, calls))),
    ) as client:
        assert type(client.realtime.calls).create is Calls.create
        response = client.realtime.calls.with_raw_response.create(**request_args(mode))
        assert response.status_code == 201
        assert response.headers["location"].endswith("/test-call")
        assert response.parse().text == ANSWER
        assert len(calls) == 2


@pytest.mark.parametrize("mode", MODES)
async def test_public_async_create_uses_generated_wire_contract(mode: str) -> None:
    calls: list[httpx2.Request] = []
    async with AsyncOpenAI(
        api_key="synthetic-test-key",
        base_url="https://example.test/v1",
        max_retries=1,
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler_for(mode, calls))),
    ) as client:
        assert type(client.realtime.calls).create is AsyncCalls.create
        response = await client.realtime.calls.with_raw_response.create(**request_args(mode))
        assert response.status_code == 201
        assert response.headers["location"].endswith("/test-call")
        assert response.parse().text == ANSWER
        assert len(calls) == 2
