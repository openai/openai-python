from __future__ import annotations

import time
import asyncio
import datetime
import threading
import traceback
from typing import Any
from unittest.mock import patch, create_autospec
from typing_extensions import override
from concurrent.futures import ThreadPoolExecutor

import anyio
import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, OpenAIError, APIStatusError, APITimeoutError
from tests.utils import update_env
from openai.providers import vertex


def test_responses_routing_retry_and_credential_ownership() -> None:
    requests: list[httpx2.Request] = []
    tokens = iter(["fake-1", "fake-2", "fake-3", "fake-4", "fake-5"])

    def handle(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        if len(requests) == 1:
            return httpx2.Response(429, json={"error": {"message": "try again"}}, headers={"retry-after-ms": "1"})
        return httpx2.Response(200, json={"id": "resp_123", "object": "response", "output": []})

    with update_env(OPENAI_API_KEY="fake-openai", OPENAI_BASE_URL="https://wrong.invalid/v1"):
        client = OpenAI(
            provider=vertex(project="test-project", location="us-east5", token_provider=lambda: next(tokens)),
            http_client=httpx2.Client(transport=httpx2.MockTransport(handle)),
        )
        client.responses.create(model="enabled-model", input="hi")
        client.responses.retrieve("resp_123")
        client.responses.delete("resp_123")
        client.responses.compact(model="enabled-model", input="hi")

    prefix = "/v1/projects/test-project/locations/us-east5/publishers/openai/v1/responses"
    assert [(r.method, r.url.path) for r in requests] == [
        ("POST", prefix),
        ("POST", prefix),
        ("GET", prefix + "/resp_123"),
        ("DELETE", prefix + "/resp_123"),
        ("POST", prefix + "/compact"),
    ]
    assert [r.headers["authorization"] for r in requests] == [f"Bearer fake-{i}" for i in range(1, 6)]
    assert all(r.url.host == "us-east5-aiplatform.googleapis.com" for r in requests)


def test_lifecycle_route_preserves_escaped_response_id_and_query() -> None:
    response = httpx2.Response(200, json={"id": "resp_123", "output": []})
    with OpenAI(
        provider=vertex(project="test-project", location="global", token_provider=lambda: "fake"),
        http_client=httpx2.Client(transport=httpx2.MockTransport(lambda _: response)),
    ) as client:
        client.responses.retrieve("resp_123/input_items", extra_query={"cursor": "a/b"})

    assert response.request.url.raw_path == (
        b"/v1/projects/test-project/locations/global/publishers/openai/v1/responses/resp_123%2Finput_items?cursor=a%2Fb"
    )


@pytest.mark.asyncio
async def test_lifecycle_route_preserves_configured_api_root() -> None:
    response = httpx2.Response(200, json={"id": "resp_123", "object": "response.deleted", "deleted": True})
    base_url = "https://gateway.invalid/v1/projects/project/locations/global/publishers/openai/v1"
    async with AsyncOpenAI(
        provider=vertex(base_url=base_url, token_provider=lambda: "fake"),
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(lambda _: response)),
    ) as client:
        await client.responses.delete("resp_123")

    assert str(response.request.url) == f"{base_url}/responses/resp_123"


@pytest.mark.parametrize(
    "location,host", [("global", "aiplatform.googleapis.com"), ("us-east5", "us-east5-aiplatform.googleapis.com")]
)
def test_derived_vertex_host_is_used_by_all_response_routes(location: str, host: str) -> None:
    seen: list[httpx2.Request] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        seen.append(request)
        return httpx2.Response(200, json={"id": "resp_test", "object": "response", "output": []})

    with update_env(GOOGLE_CLOUD_PROJECT="env-project", GOOGLE_CLOUD_LOCATION=location):
        with OpenAI(
            provider=vertex(token_provider=lambda: "fake"),
            http_client=httpx2.Client(transport=httpx2.MockTransport(handle)),
        ) as client:
            client.responses.create(model="model", input="hi", store=False)
            client.responses.retrieve("resp_test")
            client.responses.delete("resp_test")
            client.responses.compact(model="model", input="hi")
    prefix = f"/v1/projects/env-project/locations/{location}/publishers/openai/v1/responses"
    assert [(r.url.host, r.method, r.url.path) for r in seen] == [
        (host, "POST", prefix),
        (host, "GET", prefix + "/resp_test"),
        (host, "DELETE", prefix + "/resp_test"),
        (host, "POST", prefix + "/compact"),
    ]


@pytest.mark.parametrize(
    "project,env_project",
    [("example.com:my-project", "unused-project"), (None, "example.com:my-project")],
    ids=["explicit", "environment"],
)
def test_domain_scoped_project_routes_as_one_path_segment(project: str | None, env_project: str) -> None:
    response = httpx2.Response(200, json={"id": "resp_test", "object": "response", "output": []})
    with update_env(GOOGLE_CLOUD_PROJECT=env_project):
        with OpenAI(
            provider=vertex(project=project, location="global", token_provider=lambda: "fake"),
            http_client=httpx2.Client(transport=httpx2.MockTransport(lambda _: response)),
        ) as client:
            client.responses.retrieve("resp_test")

    assert str(response.request.url) == (
        "https://aiplatform.googleapis.com/v1/projects/example.com:my-project/locations/global/"
        "publishers/openai/v1/responses/resp_test"
    )


@pytest.mark.parametrize("project", [".", ".."])
def test_rejects_project_dot_path_segments(project: str) -> None:
    with pytest.raises(OpenAIError, match="project ID"):
        vertex(project=project, location="global")


@pytest.mark.asyncio
async def test_global_vertex_async_and_explicit_root() -> None:
    seen: list[str] = []

    async def handle(request: httpx2.Request) -> httpx2.Response:
        assert request.headers["authorization"] == "Bearer fake"
        seen.append(str(request.url))
        return httpx2.Response(200, json={"id": "resp_test", "object": "response", "output": []})

    for provider in (
        vertex(project="project", location="global", token_provider=lambda: "fake"),
        vertex(
            project="unused",
            location="global",
            base_url="https://gateway.invalid/publisher/v1",
            token_provider=lambda: "fake",
        ),
        vertex(base_url="http://gateway.invalid:8080/v1", token_provider=lambda: "fake"),
    ):
        async with AsyncOpenAI(
            provider=provider, http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handle))
        ) as client:
            await client.responses.create(model="model", input="hi", store=False)
    assert seen == [
        "https://aiplatform.googleapis.com/v1/projects/project/locations/global/publishers/openai/v1/responses",
        "https://gateway.invalid/publisher/v1/responses",
        "http://gateway.invalid:8080/v1/responses",
    ]


@pytest.mark.parametrize(
    "base_url",
    ["http://aiplatform.googleapis.com/v1", "http://aiplatform.googleapis.com./v1", "http://googleapis.com/v1"],
)
def test_google_vertex_endpoints_require_https(base_url: str) -> None:
    with pytest.raises(OpenAIError, match="HTTPS"):
        vertex(base_url=base_url, token_provider=lambda: "fake")


@pytest.mark.parametrize("client_cls", [OpenAI, AsyncOpenAI])
def test_vertex_rejects_openai_residency_at_construction_and_copy(client_cls: type[OpenAI] | type[AsyncOpenAI]) -> None:
    calls = 0

    def token() -> str:
        nonlocal calls
        calls += 1
        return "fake"

    provider = vertex(project="test", location="global", token_provider=token)
    with pytest.raises(OpenAIError, match="provider|mutually exclusive"):
        client_cls(provider=provider, data_residency="eu")
    client = client_cls(provider=provider)
    with pytest.raises(OpenAIError, match="provider|mutually exclusive"):
        client.with_options(data_residency="eu")
    assert calls == 0


def test_reject_cross_origin_and_redirect_without_resolving_extra_tokens() -> None:
    calls = 0

    def token() -> str:
        nonlocal calls
        calls += 1
        return "fake-google"

    seen: list[httpx2.Request] = []

    def redirect(request: httpx2.Request) -> httpx2.Response:
        seen.append(request)
        return httpx2.Response(302, headers={"location": "https://wrong.invalid/stolen"})

    client = OpenAI(
        provider=vertex(base_url="https://trusted.invalid/v1", token_provider=token),
        http_client=httpx2.Client(transport=httpx2.MockTransport(redirect), follow_redirects=True),
    )
    with pytest.raises(OpenAIError, match="configured origin"):
        client.get("https://wrong.invalid/stolen", cast_to=httpx2.Response)
    with pytest.raises(OpenAIError, match="owns authentication"):
        client.get("/responses", cast_to=httpx2.Response, options={"headers": {"Authorization": "Bearer fake-user"}})
    with pytest.raises(APIStatusError) as caught:
        client.get("/responses", cast_to=httpx2.Response)
    assert caught.value.status_code == 302
    assert calls == 1
    assert len(seen) == 1


@pytest.mark.asyncio
async def test_async_stream_boundary_and_origin_with_loop_bound_token() -> None:
    def token() -> asyncio.Future[str]:
        future: asyncio.Future[str] = asyncio.get_running_loop().create_future()
        future.set_result("fake-async")
        return future

    seen: list[httpx2.Request] = []

    async def handle(request: httpx2.Request) -> httpx2.Response:
        seen.append(request)
        return httpx2.Response(
            200,
            headers={"content-type": "text/event-stream"},
            content=b'event: response.output_text.delta\ndata: {"type":"response.output_text.delta","delta":"hi"}\n\ndata: [DONE]\n\n',
        )

    async with AsyncOpenAI(
        provider=vertex(base_url="https://trusted.invalid/v1", token_provider=token),
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handle), follow_redirects=True),
    ) as client:
        with pytest.raises(OpenAIError, match="configured origin"):
            await client.get("https://wrong.invalid/stolen", cast_to=httpx2.Response)
        stream = await client.responses.create(model="enabled-model", input="hi", stream=True)
        assert [event.delta async for event in stream if event.type == "response.output_text.delta"] == ["hi"]
    assert len(seen) == 1
    assert seen[0].headers["authorization"] == "Bearer fake-async"


def test_google_adc_and_explicit_credentials_refresh_concurrently(monkeypatch: pytest.MonkeyPatch) -> None:
    google = pytest.importorskip("google.auth")
    from google.auth.credentials import Credentials

    class FakeGoogleCredentials(Credentials):
        """Exercise Google's before_request, expiry and quota logic without any credentials/network."""

        def __init__(self) -> None:
            super().__init__()
            self._quota_project_id = "fake-quota"
            self.refreshes = 0
            self.barrier = threading.Event()
            self.barrier.set()

        @override
        def refresh(self, request: object) -> None:
            self.barrier.wait()
            self.refreshes += 1
            self.token = f"fake-refreshed-{self.refreshes}"
            self.expiry = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(
                hours=1
            )

    creds = FakeGoogleCredentials()
    calls: list[dict[str, str]] = []
    discovery: list[dict[str, object]] = []

    def default(**kwargs: object) -> tuple[Credentials, str]:
        discovery.append(kwargs)
        return creds, "fake-project"

    monkeypatch.setattr(google, "default", default)

    def handle(request: httpx2.Request) -> httpx2.Response:
        calls.append(dict(request.headers))
        return httpx2.Response(200, json={"id": "resp_fake", "output": []})

    with OpenAI(
        provider=vertex(base_url="https://trusted.invalid/v1"),
        http_client=httpx2.Client(transport=httpx2.MockTransport(handle)),
    ) as client:

        def create_response(_: int) -> object:
            return client.responses.create(model="customer-model", input="hello")

        with ThreadPoolExecutor(max_workers=5) as pool:
            list(pool.map(create_response, range(8)))
        creds.expiry = datetime.datetime(2000, 1, 1)
        client.responses.create(model="customer-model", input="hello")
    assert len(discovery) == 1
    assert creds.refreshes == 2
    assert all(h["x-goog-user-project"] == "fake-quota" for h in calls)
    assert calls[-1]["authorization"] == "Bearer fake-refreshed-2"

    with OpenAI(
        provider=vertex(base_url="https://trusted.invalid/v1", credentials=creds),
        http_client=httpx2.Client(transport=httpx2.MockTransport(handle)),
    ) as client:
        client.responses.create(model="customer-model", input="hello")
    assert len(discovery) == 1
    with pytest.raises(OpenAIError, match="only one"):
        vertex(credentials=creds, token_provider=lambda: "fake")


def test_explicit_service_account_credentials_receive_cloud_platform_scope() -> None:
    pytest.importorskip("google.auth")
    from google.auth.crypt import Signer
    from google.oauth2.service_account import Credentials

    credentials = Credentials(
        create_autospec(Signer, instance=True), "test@example.invalid", "https://accounts.invalid/token"
    )

    def refresh(scoped: Credentials, _request: object) -> None:
        assert "https://www.googleapis.com/auth/cloud-platform" in (scoped.scopes or ())
        scoped.token = "fake-scoped-token"

    response = httpx2.Response(200, json={"id": "resp_test", "output": []})
    with (
        patch.object(Credentials, "refresh", autospec=True, side_effect=refresh),
        OpenAI(
            provider=vertex(base_url="https://trusted.invalid/v1", credentials=credentials),
            http_client=httpx2.Client(transport=httpx2.MockTransport(lambda _: response)),
        ) as client,
    ):
        client.responses.create(model="model", input="hello")
    assert response.request.headers["authorization"] == "Bearer fake-scoped-token"


@pytest.mark.asyncio
@pytest.mark.parametrize("async_client", [False, True])
@pytest.mark.parametrize("connect,read", [(0.001, 1.0), (1.0, 0.001), (None, 1.0), (1.0, None), (None, None)])
async def test_google_auth_preserves_transport_timeout_phases(
    async_client: bool,
    connect: float | None,
    read: float | None,
) -> None:
    pytest.importorskip("google.auth")
    import requests
    from google.oauth2.credentials import Credentials

    credentials = Credentials(
        token=None,
        refresh_token="fake-refresh",
        token_uri="https://accounts.invalid/token",
        client_id="fake-client",
        client_secret="fake-secret",
    )

    def refresh_response(*_args: object, **kwargs: object) -> requests.Response:
        assert kwargs["timeout"] == (connect, read)
        # The transport owns the phases; elapsed authentication time must not be
        # compared against the smaller phase's timeout by the provider.
        time.sleep(0.02)
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"access_token":"fake-refreshed","expires_in":3600,"token_type":"Bearer"}'
        return response

    def handle(request: httpx2.Request) -> httpx2.Response:
        assert request.headers["authorization"] == "Bearer fake-refreshed"
        return httpx2.Response(200, json={"id": "resp_fixture", "output": []})

    provider = vertex(base_url="https://vertex.invalid/v1", credentials=credentials)
    timeout = httpx2.Timeout(1, connect=connect, read=read)
    with patch.object(requests.Session, "request", side_effect=refresh_response) as refresh_mock:
        if async_client:
            async with AsyncOpenAI(
                provider=provider,
                timeout=timeout,
                max_retries=0,
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handle)),
            ) as client:
                await client.responses.create(model="fixture", input="hi")
        else:
            with OpenAI(
                provider=provider,
                timeout=timeout,
                max_retries=0,
                http_client=httpx2.Client(transport=httpx2.MockTransport(handle)),
            ) as sync_client:
                sync_client.responses.create(model="fixture", input="hi")
        assert refresh_mock.call_count == 1


def test_sync_google_auth_refresh_timeout_is_api_timeout() -> None:
    google = pytest.importorskip("google.auth")
    requests = pytest.importorskip("requests")
    from google.oauth2.credentials import Credentials

    credentials = Credentials(
        token=None,
        refresh_token="fake-refresh-token",
        token_uri="https://accounts.invalid/token",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
    )
    with (
        patch.object(google, "default", return_value=(credentials, "fake-project")),
        patch.object(requests.Session, "request", side_effect=requests.exceptions.ReadTimeout("fake-sensitive-data")),
        OpenAI(
            provider=vertex(project="fake-project", location="global"),
            timeout=1,
            max_retries=0,
            http_client=httpx2.Client(
                transport=httpx2.MockTransport(lambda _: pytest.fail("request was dispatched after refresh timed out"))
            ),
        ) as client,
    ):
        with pytest.raises(APITimeoutError) as caught:
            client.responses.create(model="customer-model", input="hello")
    assert "fake-sensitive-data" not in "".join(traceback.format_exception(caught.value))


@pytest.mark.asyncio
async def test_auth_deadline_and_openai_header_boundaries() -> None:
    sent: list[httpx2.Request] = []

    async def handle(request: httpx2.Request) -> httpx2.Response:
        sent.append(request)
        return httpx2.Response(200, json={})

    async def waiting_token() -> str:
        await anyio.sleep_forever()
        return "fake"

    async with AsyncOpenAI(
        provider=vertex(base_url="https://trusted.invalid/v1", token_provider=waiting_token),
        timeout=0.01,
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handle)),
    ) as client:
        with pytest.raises(APITimeoutError):
            await client.responses.create(model="customer-model", input="hello")
        with pytest.raises(OpenAIError, match="OpenAI project"):
            await client.responses.create(
                model="customer-model", input="hello", extra_headers={"OpenAI-Project": "explicit-project"}
            )
    assert not sent


def test_async_google_auth_cancellation_stops_waiting_on_trio() -> None:
    pytest.importorskip("google.auth")
    from google.auth.credentials import Credentials

    started = threading.Event()
    release = threading.Event()
    finished = threading.Event()

    def block_auth(*_args: object) -> None:
        started.set()
        release.wait(timeout=2)
        finished.set()

    credentials = create_autospec(Credentials, instance=True)
    credentials.before_request.side_effect = block_auth

    async def run() -> None:
        async def handle(_request: httpx2.Request) -> httpx2.Response:
            pytest.fail("request was dispatched after authentication timed out")

        async with AsyncOpenAI(
            provider=vertex(base_url="https://trusted.invalid/v1", credentials=credentials),
            timeout=0.3,
            max_retries=0,
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handle)),
        ) as client:
            with pytest.raises(TimeoutError), anyio.fail_after(0.3):
                await client.responses.create(model="customer-model", input="hello")
            assert started.is_set()
            assert not finished.is_set()

    try:
        anyio.run(run, backend="trio")
    finally:
        release.set()
        finished.wait(timeout=2)


@pytest.mark.parametrize("backend", ["asyncio", "trio"])
def test_async_token_callback_deadline_prevents_dispatch(backend: str) -> None:
    def token() -> str:
        time.sleep(0.1)
        return "fake-token"

    async def scenario() -> None:
        async with AsyncOpenAI(
            provider=vertex(base_url="https://trusted.invalid/v1", token_provider=token),
            timeout=0.01,
            max_retries=0,
            http_client=httpx2.AsyncClient(
                transport=httpx2.MockTransport(lambda _: pytest.fail("request was dispatched after the auth deadline"))
            ),
        ) as client:
            with pytest.raises(APITimeoutError):
                await client.responses.create(model="caller-model", input="hello")

    anyio.run(scenario, backend=backend)


def test_tools_and_stream_error_use_responses_contract_without_replay() -> None:
    import json

    from openai import APIError

    bodies: list[dict[str, Any]] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        body = json.loads(request.content)
        bodies.append(body)
        if body.get("stream"):
            return httpx2.Response(
                200,
                headers={"content-type": "text/event-stream"},
                content=b'event: response.output_text.delta\ndata: {"type":"response.output_text.delta","delta":"ok"}\n\nevent: error\ndata: {"error":{"code":"unsupported_feature","message":"fake-error"}}\n\n',
            )
        if len(bodies) == 1:
            return httpx2.Response(
                200,
                json={
                    "id": "resp_fake",
                    "object": "response",
                    "output": [
                        {
                            "type": "function_call",
                            "id": "fc_fake",
                            "call_id": "call_fake",
                            "name": "get_temperature",
                            "arguments": "{}",
                        }
                    ],
                },
            )
        return httpx2.Response(200, json={"id": "resp_second", "object": "response", "output": []})

    with OpenAI(
        provider=vertex(base_url="https://trusted.invalid/v1", token_provider=lambda: "fake"),
        http_client=httpx2.Client(transport=httpx2.MockTransport(handle)),
    ) as client:
        response = client.responses.create(
            model="customer-model",
            input="temperature?",
            tools=[
                {
                    "type": "function",
                    "name": "get_temperature",
                    "parameters": {"type": "object", "properties": {}},
                    "strict": None,
                }
            ],
        )
        tool = response.output[0]
        assert tool.type == "function_call"
        client.responses.create(
            model="customer-model", input=[{"type": "function_call_output", "call_id": tool.call_id, "output": "21"}]
        )
        assert bodies[1]["input"][0] == {"type": "function_call_output", "call_id": "call_fake", "output": "21"}
        with client.responses.create(model="customer-model", input="hello", stream=True) as stream:
            iterator = iter(stream)
            event = next(iterator)
            assert event.type == "response.output_text.delta"
            assert event.delta == "ok"
            with pytest.raises(APIError, match="fake-error"):
                next(iterator)
    assert len(bodies) == 3


def test_google_auth_lock_wait_uses_pool_timeout() -> None:
    pytest.importorskip("google.auth")
    from google.auth.credentials import Credentials

    started = threading.Event()
    release = threading.Event()
    credentials = create_autospec(Credentials, instance=True)

    def block_auth(_request: object, _method: str, _url: str, headers: dict[str, str]) -> None:
        started.set()
        assert release.wait(timeout=2)
        headers["authorization"] = "Bearer fake-token"

    credentials.before_request.side_effect = block_auth
    response = httpx2.Response(200, json={"id": "resp_test", "output": []})
    with (
        OpenAI(
            provider=vertex(base_url="https://trusted.invalid/v1", credentials=credentials),
            timeout=httpx2.Timeout(1, pool=0.01),
            max_retries=0,
            http_client=httpx2.Client(transport=httpx2.MockTransport(lambda _: response)),
        ) as client,
        ThreadPoolExecutor(max_workers=1) as pool,
    ):
        first = pool.submit(client.responses.create, model="fixture", input="hi")
        try:
            assert started.wait(timeout=1)
            with pytest.raises(APITimeoutError):
                client.responses.create(model="fixture", input="hi")
        finally:
            release.set()
        assert first.result(timeout=2).id == "resp_test"
    assert credentials.before_request.call_count == 1
