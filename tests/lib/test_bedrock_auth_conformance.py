from __future__ import annotations

import json
import base64
import hashlib
import logging
import threading
from typing import Any, Iterator, AsyncIterator, cast
from pathlib import Path
from datetime import datetime

import httpx
import pytest
import jsonschema

from openai import OpenAI, AsyncOpenAI, OpenAIError, APIStatusError
from openai._utils import SensitiveHeadersFilter
from openai.providers import bedrock
from openai.lib.bedrock import BedrockOpenAI
from openai.lib._bedrock_auth import BedrockAwsAuth, BedrockAwsAuthConfig

FIXTURE_PATH = Path(__file__).parents[1] / "fixtures" / "bedrock_auth" / "v1" / "cases.json"
SCHEMA_PATH = FIXTURE_PATH.with_name("schema.json")
SHARED_SIGV4_FIXTURE_PATH = Path(__file__).parents[1] / "fixtures" / "bedrock" / "v1" / "sigv4.json"
FIXTURES = cast(dict[str, Any], json.loads(FIXTURE_PATH.read_text()))
SCHEMA = cast(dict[str, Any], json.loads(SCHEMA_PATH.read_text()))
SHARED_SIGV4_FIXTURE = cast(dict[str, Any], json.loads(SHARED_SIGV4_FIXTURE_PATH.read_text()))


def _cases(kind: str) -> list[dict[str, Any]]:
    return [cast(dict[str, Any], case) for case in FIXTURES["cases"] if case["kind"] == kind]


def _fixed_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _freeze_botocore_time(monkeypatch: pytest.MonkeyPatch, timestamps: Iterator[datetime]) -> None:
    botocore_auth = pytest.importorskip("botocore.auth")

    if hasattr(botocore_auth, "get_current_datetime"):
        monkeypatch.setattr(botocore_auth, "get_current_datetime", lambda: next(timestamps))
        return

    class FrozenDatetime:
        @classmethod
        def utcnow(cls) -> datetime:
            return next(timestamps).replace(tzinfo=None)

    monkeypatch.setattr(botocore_auth.datetime, "datetime", FrozenDatetime)


def _lower_headers(headers: httpx.Headers | dict[str, str]) -> dict[str, str]:
    return {name.lower(): value for name, value in headers.items()}


def _canonical_request_sha256(case: dict[str, Any], signed_headers: dict[str, str], payload_hash: str) -> str:
    request = case["given"]["request"]
    authorization = signed_headers["authorization"]
    signed_header_names = authorization.split("SignedHeaders=", 1)[1].split(",", 1)[0].split(";")
    canonical_headers = "".join(f"{name}:{' '.join(signed_headers[name].split())}\n" for name in signed_header_names)
    url = httpx.URL(request["url"])
    canonical_request = "\n".join(
        (
            request["method"],
            url.raw_path.split(b"?", 1)[0].decode(),
            url.query.decode(),
            canonical_headers,
            ";".join(signed_header_names),
            payload_hash,
        )
    )
    return hashlib.sha256(canonical_request.encode()).hexdigest()


def test_shared_sigv4_fixture_matches_node(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = SHARED_SIGV4_FIXTURE
    credentials = fixture["credentials"]
    request = fixture["request"]
    body = request["body"].encode()
    payload_hash = hashlib.sha256(body).hexdigest()
    _freeze_botocore_time(monkeypatch, iter([_fixed_datetime(fixture["signingDate"])]))

    auth = BedrockAwsAuth(
        BedrockAwsAuthConfig(
            region=fixture["region"],
            source="static",
            access_key_id=credentials["accessKeyId"],
            secret_access_key=credentials["secretAccessKey"],
            session_token=credentials["sessionToken"],
        )
    )
    signed_headers = _lower_headers(
        auth.sign(
            method=request["method"],
            url=request["url"],
            headers={
                "content-type": request["contentType"],
                "host": httpx.URL(request["url"]).host,
            },
            body=body,
        )
    )
    canonical_case = {"given": {"request": request}}

    assert fixture["service"] == "bedrock-mantle"
    assert payload_hash == fixture["expected"]["payloadHash"]
    assert (
        _canonical_request_sha256(canonical_case, signed_headers, payload_hash)
        == fixture["expected"]["canonicalRequestHash"]
    )
    assert signed_headers["authorization"] == fixture["expected"]["authorization"]
    assert signed_headers["x-amz-date"] == fixture["expected"]["date"]


@pytest.mark.parametrize("case", _cases("auth_selection"), ids=lambda case: case["id"])
def test_auth_selection_fixture(case: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AWS_BEARER_TOKEN_BEDROCK", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    for name, value in case["given"]["environment"].items():
        monkeypatch.setenv(name, value)

    explicit = case["given"]["explicit"]
    kwargs: dict[str, Any] = {
        "aws_region": "us-east-1",
        "http_client": httpx.Client(trust_env=False),
        "_enforce_credentials": False,
    }
    if "bearer" in explicit:
        kwargs["api_key"] = explicit["bearer"]
    if "aws" in explicit:
        kwargs["aws_access_key_id"] = explicit["aws"]["access_key_id"]
        kwargs["aws_secret_access_key"] = explicit["aws"]["secret_access_key"]
    if "profile" in explicit:
        kwargs["aws_profile"] = explicit["profile"]

    if case["expected"].get("error") == "bedrock_conflicting_auth":
        with pytest.raises(OpenAIError, match="authentication is ambiguous"):
            BedrockOpenAI(**kwargs)
        kwargs["http_client"].close()
        return

    with BedrockOpenAI(**kwargs) as client:
        state = client._bedrock_state
        if not client._uses_aws_auth():
            mode = "bearer"
            source = "explicit" if state.explicit_api_key is not None else "environment"
        else:
            mode = "sigv4"
            if state.aws_access_key_id is not None:
                source = "static"
            elif state.aws_profile is not None:
                source = "profile"
            elif state.aws_credentials_provider is not None:
                source = "provider"
            else:
                source = "default"

        assert mode == case["expected"]["auth_mode"]
        assert source == case["expected"]["auth_source"]


@pytest.mark.parametrize("case", _cases("sigv4"), ids=lambda case: case["id"])
def test_sigv4_fixture(case: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    credentials = case["given"]["credentials"]
    signing = case["given"]["signing"]
    request = case["given"]["request"]
    body = base64.b64decode(request["body_base64"])
    payload_hash = hashlib.sha256(body).hexdigest()

    auth = BedrockAwsAuth(
        BedrockAwsAuthConfig(
            region=signing["region"],
            source="static",
            access_key_id=credentials["access_key_id"],
            secret_access_key=credentials["secret_access_key"],
            session_token=credentials.get("session_token"),
        )
    )
    _freeze_botocore_time(monkeypatch, iter([_fixed_datetime(signing["timestamp"])]))

    signed_headers = _lower_headers(
        auth.sign(
            method=request["method"],
            url=request["url"],
            headers=request["headers"],
            body=body,
        )
    )

    assert signing["service"] == "bedrock-mantle"
    assert payload_hash == case["expected"]["payload_sha256"]
    assert _canonical_request_sha256(case, signed_headers, payload_hash) == case["expected"]["canonical_request_sha256"]
    for name, value in case["expected"]["headers"].items():
        assert signed_headers[name] == value


class _Credentials:
    def __init__(self, access_key: str, secret_key: str, token: str | None = None) -> None:
        self.access_key = access_key
        self.secret_key = secret_key
        self.token = token


def test_retry_signing_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    case = _cases("retry_signing")[0]
    timestamps = iter(_fixed_datetime(value) for value in case["given"]["timestamps"])
    credentials = iter(
        _Credentials(access_key, f"{access_key}-secret") for access_key in case["given"]["access_key_ids"]
    )
    provider_calls = 0

    def credentials_provider() -> _Credentials:
        nonlocal provider_calls
        provider_calls += 1
        return next(credentials)

    _freeze_botocore_time(monkeypatch, timestamps)

    requests: list[httpx.Request] = []
    statuses = iter(case["given"]["response_statuses"])

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(next(statuses), request=request, json={})

    body = base64.b64decode(case["given"]["body_base64"])
    with OpenAI(
        provider=bedrock(
            base_url="https://bedrock-mantle.us-east-1.api.aws/openai/v1",
            region="us-east-1",
            credential_provider=credentials_provider,
        ),
        max_retries=case["given"].get("max_retries", 1),
        http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
    ) as client:
        client.post(
            "/responses",
            content=body,
            cast_to=httpx.Response,
            options={"headers": {"Content-Type": "application/json"}},
        )

    assert len(requests) == case["expected"]["attempts"]
    assert provider_calls == case["expected"]["credential_provider_calls"]
    assert [request.headers["X-Amz-Date"] for request in requests] == case["expected"]["x_amz_dates"]
    assert [hashlib.sha256(request.content).hexdigest() for request in requests] == case["expected"]["body_sha256"]
    for request, access_key in zip(requests, case["given"]["access_key_ids"]):
        assert f"Credential={access_key}/" in request.headers["Authorization"]


@pytest.mark.parametrize("case", _cases("body_replay"), ids=lambda case: case["id"])
def test_body_replay_fixture(case: dict[str, Any]) -> None:
    provider_calls = 0
    network_calls = 0
    body_reads = 0
    requests: list[httpx.Request] = []

    def credentials_provider() -> _Credentials:
        nonlocal provider_calls
        provider_calls += 1
        return _Credentials("access-key", "secret-key")

    def body() -> Iterator[bytes]:
        nonlocal body_reads
        body_reads += 1
        for chunk in case["given"].get("chunks_base64", []):
            yield base64.b64decode(chunk)

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal network_calls
        network_calls += 1
        requests.append(request)
        statuses = case["given"].get("response_statuses", [200])
        return httpx.Response(statuses[network_calls - 1], request=request, json={})

    body_kind = case["given"]["body_kind"]
    content: bytes | Iterator[bytes]
    if body_kind == "bytes":
        content = base64.b64decode(case["given"]["body_base64"])
    else:
        assert body_kind == "one_shot_stream"
        content = body()

    with OpenAI(
        provider=bedrock(
            base_url="https://bedrock-mantle.us-east-1.api.aws/openai/v1",
            region="us-east-1",
            credential_provider=credentials_provider,
        ),
        max_retries=case["given"].get("max_retries", 1),
        http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
    ) as client:
        if case["expected"]["result"] == "bedrock_non_replayable_body":
            with pytest.raises(OpenAIError, match="requires a replayable request body"):
                client.post("/responses", content=content, cast_to=httpx.Response)
        else:
            client.post("/responses", content=content, cast_to=httpx.Response)

    assert network_calls == case["expected"].get("network_attempts", case["expected"].get("attempts"))
    if body_kind == "bytes":
        assert all(request.content == content for request in requests)
        assert provider_calls == case["expected"]["attempts"]
    else:
        assert (body_reads, provider_calls) == (0, 0)


@pytest.mark.asyncio
async def test_non_replayable_async_body_fails_before_credentials_or_network() -> None:
    provider_calls = 0
    network_calls = 0
    body_reads = 0

    def credentials_provider() -> _Credentials:
        nonlocal provider_calls
        provider_calls += 1
        return _Credentials("access-key", "secret-key")

    async def body() -> AsyncIterator[bytes]:
        nonlocal body_reads
        body_reads += 1
        yield b"body"

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal network_calls
        network_calls += 1
        return httpx.Response(200, request=request)

    async with AsyncOpenAI(
        provider=bedrock(
            base_url="https://bedrock-mantle.us-east-1.api.aws/openai/v1",
            region="us-east-1",
            credential_provider=credentials_provider,
        ),
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler), trust_env=False),
    ) as client:
        with pytest.raises(OpenAIError, match="requires a replayable request body"):
            await client.post("/responses", content=body(), cast_to=httpx.Response)

    assert (body_reads, provider_calls, network_calls) == (0, 0, 0)


@pytest.mark.asyncio
async def test_async_credentials_are_resolved_off_event_loop() -> None:
    event_loop_thread = threading.get_ident()
    provider_threads: list[int] = []

    def credentials_provider() -> _Credentials:
        provider_threads.append(threading.get_ident())
        return _Credentials("access-key", "secret-key")

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, request=request, json={})

    async with AsyncOpenAI(
        provider=bedrock(
            base_url="https://bedrock-mantle.us-east-1.api.aws/openai/v1",
            region="us-east-1",
            credential_provider=credentials_provider,
        ),
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler), trust_env=False),
    ) as client:
        await client.post("/responses", content=b"{}", cast_to=httpx.Response)

    assert provider_threads
    assert all(thread_id != event_loop_thread for thread_id in provider_threads)


def test_custom_http_client_auth_cannot_replace_sigv4() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, request=request, json={})

    with OpenAI(
        provider=bedrock(
            base_url="https://bedrock-mantle.us-east-1.api.aws/openai/v1",
            region="us-east-1",
            access_key_id="access-key",
            secret_access_key="secret-key",
        ),
        http_client=httpx.Client(
            auth=httpx.BasicAuth("username", "password"),
            transport=httpx.MockTransport(handler),
            trust_env=False,
        ),
    ) as client:
        client.get("/models", cast_to=httpx.Response)

    assert requests[0].headers["Authorization"].startswith("AWS4-HMAC-SHA256 Credential=access-key/")


def test_sigv4_redirects_are_not_followed() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if len(requests) == 1:
            return httpx.Response(307, request=request, headers={"Location": "/redirected"})
        return httpx.Response(200, request=request)

    with OpenAI(
        provider=bedrock(
            base_url="https://bedrock-mantle.us-east-1.api.aws/openai/v1",
            region="us-east-1",
            access_key_id="access-key",
            secret_access_key="secret-key",
        ),
        http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
    ) as client:
        with pytest.raises(APIStatusError) as exc:
            client.get("/models", cast_to=httpx.Response)

    assert exc.value.status_code == 307
    assert len(requests) == 1


def test_redaction_fixture(caplog: pytest.LogCaptureFixture) -> None:
    case = _cases("redaction")[0]
    logger = logging.getLogger("test_bedrock_redaction")
    logger.addFilter(SensitiveHeadersFilter())

    with caplog.at_level(logging.DEBUG):
        logger.debug("Request options: %s", {"headers": case["given"]["headers"]})

    headers = cast(dict[str, Any], caplog.records[0].args)["headers"]
    assert headers == case["expected"]["headers"]
    for value in case["expected"]["forbidden_substrings"]:
        assert value not in caplog.messages[0]


def test_fixture_envelope_is_versioned_and_ids_are_unique() -> None:
    jsonschema.Draft202012Validator(SCHEMA).validate(FIXTURES)  # pyright: ignore[reportUnknownMemberType]
    assert FIXTURES["schema_version"] == 1
    assert FIXTURES["suite"] == "aws-bedrock-auth"
    ids = [case["id"] for case in FIXTURES["cases"]]
    assert len(ids) == len(set(ids))
