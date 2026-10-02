from __future__ import annotations

import sys
import json
from types import SimpleNamespace
from typing import Any, Literal
from pathlib import Path
from typing_extensions import override

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, OpenAIError, NotFoundError
from openai.providers import bedrock
from openai.lib.bedrock import BedrockOpenAI, AsyncBedrockOpenAI

_MODELS = (
    "us.openai.gpt-5.6-sol",
    "us.openai.gpt-5.6-terra",
    "us.openai.gpt-5.6-luna",
)
_MODEL = _MODELS[0]
_RUNTIME_URL = "https://bedrock-runtime.us-east-1.amazonaws.com/openai/v1"
_PARTITIONS = [
    ("mantle", "us-east-1", "api.aws", "api.aws"),
    ("runtime", "us-east-1", "amazonaws.com", "api.aws"),
    ("runtime", "cn-north-1", "amazonaws.com.cn", "api.amazonwebservices.com.cn"),
    ("runtime", "eusc-de-east-1", "amazonaws.eu", "api.amazonwebservices.eu"),
    ("runtime", "us-iso-east-1", "c2s.ic.gov", "api.aws.ic.gov"),
    ("runtime", "us-isob-east-1", "sc2s.sgov.gov", "api.aws.scloud"),
    ("runtime", "eu-isoe-west-1", "cloud.adc-e.uk", "api.cloud-aws.adc-e.uk"),
    ("runtime", "us-isof-south-1", "csp.hci.ic.gov", "api.aws.hci.ic.gov"),
]
_AWS_ENVIRONMENT = (
    "AWS_REGION",
    "AWS_DEFAULT_REGION",
    "AWS_BEDROCK_BASE_URL",
    "AWS_BEARER_TOKEN_BEDROCK",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "AWS_PROFILE",
    "AWS_DEFAULT_PROFILE",
)


@pytest.fixture(autouse=True)
def clean_aws_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in _AWS_ENVIRONMENT:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")


def _provider(authentication: Literal["bearer", "sigv4"], **options: Any) -> Any:
    if authentication == "bearer":
        return bedrock(api_key="bedrock-token", **options)
    return bedrock(access_key_id="access-key", secret_access_key="secret-key", **options)


def _assert_authorization(request: httpx2.Request, authentication: str, *, service: str = "bedrock") -> None:
    authorization = request.headers["Authorization"]
    if authentication == "bearer":
        assert authorization == "Bearer bedrock-token"
    else:
        assert f"/{service}/aws4_request" in authorization


def _completion_body(
    *, model: str = _MODEL, content: str = "Hello", finish_reason: str | None = "stop"
) -> dict[str, Any]:
    return {
        "id": "chatcmpl_runtime",
        "object": "chat.completion",
        "created": 1,
        "model": model,
        "choices": [{"index": 0, "finish_reason": finish_reason, "message": {"role": "assistant", "content": content}}],
        "usage": {"prompt_tokens": 4, "completion_tokens": 3, "total_tokens": 7},
    }


def _response_body(*, model: str = _MODEL) -> dict[str, Any]:
    return {
        "id": "resp_runtime",
        "object": "response",
        "model": model,
        "status": "completed",
        "output": [
            {
                "id": "msg_runtime",
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [{"type": "output_text", "text": "Hello", "annotations": []}],
            }
        ],
    }


def _sse(events: list[dict[str, Any] | str]) -> str:
    return "".join(f"data: {event if isinstance(event, str) else json.dumps(event)}\n\n" for event in events)


@pytest.mark.parametrize(("endpoint", "region", "suffix", "dual_stack_suffix"), _PARTITIONS)
@pytest.mark.parametrize("authentication", ["bearer", "sigv4"])
def test_canonical_endpoint_partitions_and_security(
    endpoint: Literal["mantle", "runtime"],
    region: str,
    suffix: str,
    dual_stack_suffix: str,
    authentication: Literal["bearer", "sigv4"],
) -> None:
    default_client = OpenAI(provider=_provider(authentication, endpoint=endpoint, region=region))
    assert default_client.base_url.host == f"bedrock-{endpoint}.{region}.{suffix}"

    hostnames = (
        [f"bedrock-mantle.{region}.{suffix}"]
        if endpoint == "mantle"
        else [
            f"{service}.{region}.{dns_suffix}"
            for dns_suffix in (suffix, dual_stack_suffix)
            for service in ("bedrock-runtime", "bedrock-runtime-fips")
        ]
    )
    for hostname in hostnames:
        base_url = f"https://{hostname}./openai/v1"
        client = OpenAI(provider=_provider(authentication, endpoint=endpoint, region=region, base_url=base_url))
        assert client.base_url.host == f"{hostname}."

        if endpoint == "runtime":
            inferred = OpenAI(provider=_provider(authentication, region=region, base_url=base_url))
            assert inferred.base_url.host == f"{hostname}."

        with pytest.raises(OpenAIError, match="HTTPS"):
            _provider(authentication, endpoint=endpoint, region=region, base_url=f"http://{hostname}./openai/v1")
        with pytest.raises(OpenAIError, match="does not match the selected"):
            _provider(
                authentication,
                endpoint="runtime" if endpoint == "mantle" else "mantle",
                region=region,
                base_url=base_url,
            )
        with pytest.raises(OpenAIError, match="endpoint region.*does not match"):
            _provider(
                authentication,
                endpoint=endpoint,
                region="us-west-2" if region == "us-east-1" else "us-east-1",
                base_url=base_url,
            )


@pytest.mark.parametrize("authentication", ["bearer", "sigv4"])
@pytest.mark.parametrize("api", ["chat", "responses"])
@pytest.mark.parametrize("model", _MODELS)
def test_runtime_routes_and_authenticates_nonstreaming_apis(
    authentication: Literal["bearer", "sigv4"], api: Literal["chat", "responses"], model: str
) -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(
            200,
            request=request,
            json=_completion_body(model=model) if api == "chat" else _response_body(model=model),
            headers={"x-request-id": "req_runtime"},
        )

    with OpenAI(
        provider=_provider(authentication, endpoint="runtime", region="us-east-1"),
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
    ) as client:
        if api == "chat":
            completion = client.chat.completions.create(model=model, messages=[{"role": "user", "content": "Hi"}])
            assert completion.choices[0].finish_reason == "stop"
            assert completion.usage is not None and completion.usage.total_tokens == 7
            assert completion._request_id == "req_runtime"
        else:
            response = client.responses.create(model=model, input="Hi")
            assert response.output_text == "Hello"

    route = "chat/completions" if api == "chat" else "responses"
    assert str(requests[0].url) == f"{_RUNTIME_URL}/{route}"
    assert json.loads(requests[0].content)["model"] == model
    _assert_authorization(requests[0], authentication)


@pytest.mark.parametrize("authentication", ["bearer", "sigv4"])
@pytest.mark.parametrize("api", ["chat", "responses"])
@pytest.mark.parametrize("model", _MODELS)
def test_runtime_streams_both_apis_with_both_authentication_modes(
    authentication: Literal["bearer", "sigv4"], api: Literal["chat", "responses"], model: str
) -> None:
    requests: list[httpx2.Request] = []
    if api == "chat":
        chunks = [
            {
                "id": "chatcmpl_runtime",
                "object": "chat.completion.chunk",
                "created": 1,
                "model": model,
                "choices": [{"index": 0, "delta": delta, "finish_reason": finish_reason}],
            }
            for delta, finish_reason in (({"role": "assistant", "content": "Hel"}, None), ({"content": "lo"}, "stop"))
        ]
        events: list[dict[str, Any] | str] = [*chunks, "[DONE]", chunks[0]]
    else:
        completed = _response_body(model=model)
        events = [
            {"type": "response.created", "sequence_number": 0, "response": {**completed, "status": "in_progress"}},
            {"type": "response.completed", "sequence_number": 1, "response": completed},
            "[DONE]",
            {"type": "response.failed", "sequence_number": 2, "response": completed},
        ]

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, text=_sse(events), headers={"Content-Type": "text/event-stream"})

    with OpenAI(
        provider=_provider(authentication, endpoint="runtime", region="us-east-1"),
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
    ) as client:
        if api == "chat":
            stream = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": "Hi"}], stream=True
            )
            received = list(stream)
            assert [chunk.choices[0].delta.content for chunk in received] == ["Hel", "lo"]
            assert received[-1].choices[0].finish_reason == "stop"
        else:
            response_stream = client.responses.create(model=model, input="Hi", stream=True)
            received_events = list(response_stream)
            assert [event.type for event in received_events] == ["response.created", "response.completed"]

    request_body = json.loads(requests[0].content)
    assert request_body["stream"] is True
    assert request_body["model"] == model
    _assert_authorization(requests[0], authentication)


@pytest.mark.asyncio
@pytest.mark.parametrize("authentication", ["bearer", "sigv4"])
async def test_async_runtime_chat_uses_selected_authentication(authentication: Literal["bearer", "sigv4"]) -> None:
    requests: list[httpx2.Request] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json=_completion_body())

    async with AsyncOpenAI(
        provider=_provider(authentication, endpoint="runtime", region="us-east-1"),
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False),
    ) as client:
        response = await client.chat.completions.create(model=_MODEL, messages=[{"role": "user", "content": "Hi"}])

    assert response.choices[0].message.content == "Hello"
    _assert_authorization(requests[0], authentication)


@pytest.mark.asyncio
async def test_async_runtime_accepts_refreshable_async_bearer_credentials() -> None:
    tokens = iter(("async-token-one", "async-token-two"))
    authorization_headers: list[str] = []

    async def token_provider() -> str:
        return next(tokens)

    async def handler(request: httpx2.Request) -> httpx2.Response:
        authorization_headers.append(request.headers["Authorization"])
        status = 429 if len(authorization_headers) == 1 else 200
        return httpx2.Response(status, request=request, json={}, headers={"retry-after-ms": "1"})

    async with AsyncOpenAI(
        provider=bedrock(endpoint="runtime", region="us-east-1", token_provider=token_provider),
        max_retries=1,
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False),
    ) as client:
        await client.get("/models", cast_to=httpx2.Response)

    assert authorization_headers == ["Bearer async-token-one", "Bearer async-token-two"]


@pytest.mark.parametrize(
    "region",
    ["us-east-1.amazonaws.com@attacker.example#", "us-east-1/../../attacker.example", "us-east-1?target=evil"],
)
def test_runtime_rejects_injected_regions(region: str) -> None:
    with pytest.raises(OpenAIError, match="region.*invalid"):
        bedrock(endpoint="runtime", region=region, api_key="bedrock-token")


@pytest.mark.parametrize("region_environment_variable", ["AWS_REGION", "AWS_DEFAULT_REGION"])
@pytest.mark.parametrize(
    ("base_url", "ambient_region"),
    [
        pytest.param("https://proxy.example/openai/v1", "local", id="custom-url-invalid-region"),
        pytest.param(_RUNTIME_URL, "us-west-2", id="canonical-url-conflicting-region"),
    ],
)
def test_bearer_configured_url_ignores_ambient_region(
    base_url: str,
    ambient_region: str,
    region_environment_variable: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(region_environment_variable, ambient_region)

    with OpenAI(provider=bedrock(base_url=base_url, api_key="bedrock-token")) as client:
        assert client.base_url == httpx2.URL(f"{base_url}/")


@pytest.mark.parametrize(
    ("credential_source", "base_url_source"),
    [
        ("api_key", "environment"),
        ("token_provider", "argument"),
        ("environment", "argument"),
        ("environment", "environment"),
    ],
)
def test_bearer_credential_sources_ignore_conflicting_ambient_region(
    credential_source: Literal["api_key", "token_provider", "environment"],
    base_url_source: Literal["argument", "environment"],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AWS_REGION", "us-west-2")
    options: dict[str, Any] = {}

    if base_url_source == "environment":
        monkeypatch.setenv("AWS_BEDROCK_BASE_URL", _RUNTIME_URL)
    else:
        options["base_url"] = _RUNTIME_URL

    if credential_source == "api_key":
        options["api_key"] = "bedrock-token"
    elif credential_source == "token_provider":
        options["token_provider"] = lambda: "bedrock-token"
    else:
        monkeypatch.setenv("AWS_BEARER_TOKEN_BEDROCK", "bedrock-token")

    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={})

    with OpenAI(
        provider=bedrock(**options),
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
    ) as client:
        assert client.base_url == httpx2.URL(f"{_RUNTIME_URL}/")
        client.get("/models", cast_to=httpx2.Response)

    _assert_authorization(requests[0], "bearer")


@pytest.mark.anyio
@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI], ids=["sync", "async"])
@pytest.mark.parametrize("refresh", ["api-key-mutation", "api-key-copy", "token-provider-copy"])
async def test_legacy_bearer_refresh_ignores_conflicting_ambient_region(
    client_cls: type[BedrockOpenAI] | type[AsyncBedrockOpenAI],
    refresh: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AWS_REGION", "us-west-2")
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={})

    client: BedrockOpenAI | AsyncBedrockOpenAI
    if client_cls is BedrockOpenAI:
        client = BedrockOpenAI(
            base_url=_RUNTIME_URL,
            api_key="initial-token",
            http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
        )
    else:
        client = AsyncBedrockOpenAI(
            base_url=_RUNTIME_URL,
            api_key="initial-token",
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False),
        )

    assert client.aws_region == "us-west-2"
    assert not client._bedrock_state.region_was_explicit

    if refresh == "api-key-mutation":
        client.api_key = "refreshed-token"
    elif refresh == "api-key-copy":
        client = client.with_options(api_key="refreshed-token")
    else:
        client = client.with_options(bedrock_token_provider=lambda: "refreshed-token")

    if isinstance(client, BedrockOpenAI):
        client.get("/models", cast_to=httpx2.Response)
        client.close()
    else:
        await client.get("/models", cast_to=httpx2.Response)
        await client.close()

    assert requests[0].headers["Authorization"] == "Bearer refreshed-token"


@pytest.mark.anyio
@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI], ids=["sync", "async"])
@pytest.mark.parametrize(
    ("base_url", "service"),
    [
        pytest.param(_RUNTIME_URL, "bedrock", id="runtime"),
        pytest.param("https://bedrock-mantle.us-east-1.api.aws/openai/v1", "bedrock-mantle", id="mantle"),
    ],
)
async def test_legacy_canonical_bearer_region_survives_aws_credential_override(
    client_cls: type[BedrockOpenAI] | type[AsyncBedrockOpenAI], base_url: str, service: str
) -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={})

    client: BedrockOpenAI | AsyncBedrockOpenAI
    if client_cls is BedrockOpenAI:
        client = BedrockOpenAI(
            base_url=base_url,
            api_key="initial-token",
            http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
        )
    else:
        client = AsyncBedrockOpenAI(
            base_url=base_url,
            api_key="initial-token",
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False),
        )

    assert client.aws_region == "us-east-1"
    assert not client._bedrock_state.region_was_explicit
    client = client.with_options(aws_access_key_id="access-key", aws_secret_access_key="secret-key")

    if isinstance(client, BedrockOpenAI):
        client.get("/models", cast_to=httpx2.Response)
        client.close()
    else:
        await client.get("/models", cast_to=httpx2.Response)
        await client.close()

    assert f"/{service}/aws4_request" in requests[0].headers["Authorization"]


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI], ids=["sync", "async"])
@pytest.mark.parametrize(
    ("explicit_region", "expected_region", "region_was_explicit"),
    [
        pytest.param(None, "us-west-2", False, id="ambient-region"),
        pytest.param("us-east-1", "us-east-1", True, id="explicit-region"),
    ],
)
def test_legacy_canonical_region_preserves_configured_precedence(
    client_cls: type[BedrockOpenAI] | type[AsyncBedrockOpenAI],
    explicit_region: str | None,
    expected_region: str,
    region_was_explicit: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AWS_REGION", "us-west-2")

    client = client_cls(base_url=_RUNTIME_URL, aws_region=explicit_region, api_key="bedrock-token")

    assert client.aws_region == expected_region
    assert client._bedrock_state.region_was_explicit is region_was_explicit


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI], ids=["sync", "async"])
@pytest.mark.parametrize("base_url", [_RUNTIME_URL, "https://proxy.example/openai/v1"])
def test_legacy_bedrock_accepts_loaded_httpx_urls(
    client_cls: type[BedrockOpenAI] | type[AsyncBedrockOpenAI], base_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    class LegacyURL:
        @override
        def __str__(self) -> str:
            return base_url

    legacy_httpx = SimpleNamespace(URL=LegacyURL)
    monkeypatch.setitem(sys.modules, "httpx", legacy_httpx)

    client = client_cls(base_url=LegacyURL(), api_key="bedrock-token")  # type: ignore[arg-type]

    assert client.base_url == httpx2.URL(f"{base_url}/")


@pytest.mark.parametrize(
    ("region", "error"),
    [
        pytest.param("local", "region.*invalid", id="invalid-region"),
        pytest.param("us-west-2", "endpoint region.*does not match", id="conflicting-region"),
    ],
)
def test_bearer_configured_url_still_validates_explicit_region(region: str, error: str) -> None:
    with pytest.raises(OpenAIError, match=error):
        bedrock(base_url=_RUNTIME_URL, region=region, api_key="bedrock-token")


@pytest.mark.parametrize(
    ("base_url", "ambient_region", "error"),
    [
        pytest.param("https://proxy.example/openai/v1", "local", "region.*invalid", id="invalid-region"),
        pytest.param(_RUNTIME_URL, "us-west-2", "endpoint region.*does not match", id="conflicting-region"),
    ],
)
def test_sigv4_configured_url_still_validates_ambient_region(
    base_url: str, ambient_region: str, error: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AWS_REGION", ambient_region)

    with pytest.raises(OpenAIError, match=error):
        bedrock(base_url=base_url, access_key_id="access-key", secret_access_key="secret-key")


def test_runtime_infers_environment_endpoint_and_signing_service(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AWS_BEDROCK_BASE_URL", _RUNTIME_URL)
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={})

    with OpenAI(
        provider=_provider("sigv4", region="us-east-1"),
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
    ) as client:
        client.get("/models", cast_to=httpx2.Response)

    _assert_authorization(requests[0], "sigv4")


@pytest.mark.parametrize(
    ("endpoint", "source", "service"),
    [
        (None, "argument", "bedrock-mantle"),
        ("mantle", "argument", "bedrock-mantle"),
        ("runtime", "argument", "bedrock"),
        (None, "environment", "bedrock-mantle"),
        ("runtime", "environment", "bedrock"),
    ],
)
def test_custom_signing_endpoint_preserves_mantle_default_and_runtime_opt_in(
    endpoint: Literal["mantle", "runtime"] | None,
    source: Literal["argument", "environment"],
    service: Literal["bedrock-mantle", "bedrock"],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    base_url = "https://proxy.example/openai/v1"
    options: dict[str, Any] = {"region": "us-east-1"}
    if endpoint is not None:
        options["endpoint"] = endpoint
    if source == "environment":
        monkeypatch.setenv("AWS_BEDROCK_BASE_URL", base_url)
    else:
        options["base_url"] = base_url

    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={})

    with OpenAI(
        provider=_provider("sigv4", **options),
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
    ) as client:
        assert client.base_url == httpx2.URL(f"{base_url}/")
        client.get("/models", cast_to=httpx2.Response)

    assert requests[0].url == httpx2.URL(f"{base_url}/models")
    _assert_authorization(requests[0], "sigv4", service=service)


def test_runtime_api_key_none_ignores_stale_environment_bearer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AWS_BEARER_TOKEN_BEDROCK", "stale-token")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "environment-access-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "environment-secret-key")
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={})

    with OpenAI(
        provider=bedrock(endpoint="runtime", region="us-east-1", api_key=None),
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
    ) as client:
        client.get("/models", cast_to=httpx2.Response)

    assert "Credential=environment-access-key/" in requests[0].headers["Authorization"]
    _assert_authorization(requests[0], "sigv4")


def test_runtime_profile_resolves_region_and_signing_credentials(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    credentials = tmp_path / "credentials"
    credentials.write_text("[runtime]\naws_access_key_id=profile-key\naws_secret_access_key=profile-secret\n")
    config = tmp_path / "config"
    config.write_text("[profile runtime]\nregion=us-west-2\n")
    monkeypatch.setenv("AWS_SHARED_CREDENTIALS_FILE", str(credentials))
    monkeypatch.setenv("AWS_CONFIG_FILE", str(config))
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={})

    with OpenAI(
        provider=bedrock(endpoint="runtime", profile="runtime", api_key=None),
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
    ) as client:
        client.get("/models", cast_to=httpx2.Response)

    assert requests[0].url.host == "bedrock-runtime.us-west-2.amazonaws.com"
    assert "Credential=profile-key/" in requests[0].headers["Authorization"]
    assert "/us-west-2/bedrock/aws4_request" in requests[0].headers["Authorization"]


def test_runtime_preserves_request_id_on_typed_errors() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(
            404,
            request=request,
            json={"error": {"message": "Runtime model is unavailable"}},
            headers={"x-request-id": "req_runtime_error"},
        )

    with OpenAI(
        provider=_provider("bearer", endpoint="runtime", region="us-east-1"),
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
    ) as client:
        with pytest.raises(NotFoundError, match="Runtime model is unavailable") as error:
            client.chat.completions.create(model=_MODEL, messages=[{"role": "user", "content": "Hi"}])

    assert error.value.request_id == "req_runtime_error"


def test_runtime_refreshes_bearer_credentials_before_retry() -> None:
    tokens = iter(("token-one", "token-two"))
    authorization_headers: list[str] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        authorization_headers.append(request.headers["Authorization"])
        if len(authorization_headers) == 1:
            return httpx2.Response(429, request=request, json={}, headers={"retry-after-ms": "1"})
        return httpx2.Response(200, request=request, json={})

    with OpenAI(
        provider=bedrock(endpoint="runtime", region="us-east-1", token_provider=lambda: next(tokens)),
        max_retries=1,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
    ) as client:
        client.get("/models", cast_to=httpx2.Response)

    assert authorization_headers == ["Bearer token-one", "Bearer token-two"]


@pytest.mark.parametrize("failure", ["rate-limit", "timeout"])
def test_runtime_refreshes_aws_credentials_and_resigns_retries(failure: Literal["rate-limit", "timeout"]) -> None:
    class Credentials:
        def __init__(self, generation: int) -> None:
            self.access_key = f"access-{generation}"
            self.secret_key = f"secret-{generation}"
            self.token = f"session-{generation}"

    generations = iter((1, 2))
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        if len(requests) == 1:
            if failure == "timeout":
                raise httpx2.ReadTimeout("Bedrock Runtime request timed out", request=request)
            return httpx2.Response(429, request=request, json={}, headers={"retry-after-ms": "1"})
        return httpx2.Response(200, request=request, json={})

    with OpenAI(
        provider=bedrock(
            endpoint="runtime",
            region="us-east-1",
            credential_provider=lambda: Credentials(next(generations)),
            api_key=None,
        ),
        max_retries=1,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
    ) as client:
        client.get("/models", cast_to=httpx2.Response)

    assert [request.headers["X-Amz-Security-Token"] for request in requests] == ["session-1", "session-2"]
    for generation, request in enumerate(requests, start=1):
        assert f"Credential=access-{generation}/" in request.headers["Authorization"]
        _assert_authorization(request, "sigv4")


@pytest.mark.parametrize("authentication", ["bearer", "sigv4"])
def test_runtime_rejects_cross_origin_requests_before_network(authentication: Literal["bearer", "sigv4"]) -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={})

    with OpenAI(
        provider=_provider(authentication, endpoint="runtime", region="us-east-1"),
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
    ) as client:
        with pytest.raises(OpenAIError, match="origin other than the configured provider URL"):
            client.get("https://attacker.example/credentials", cast_to=httpx2.Response)

    assert not requests
