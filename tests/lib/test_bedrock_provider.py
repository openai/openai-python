from __future__ import annotations

import builtins
from typing import Any, Iterator, cast

import httpx
import pytest

import openai.lib._bedrock_auth as bedrock_auth_module
from openai import OpenAI, AsyncOpenAI, OpenAIError
from tests.utils import update_env
from openai._types import Omit
from openai._provider import _create_provider, _ProviderRuntime
from openai.providers import bedrock


def test_sync_provider_owns_endpoint_and_bearer_authentication() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, request=request, json={})

    client = OpenAI(
        provider=bedrock(region="us-east-1", api_key="bedrock token"),
        http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
    )
    client.get("/models", cast_to=httpx.Response)

    assert client.base_url == httpx.URL("https://bedrock-mantle.us-east-1.api.aws/openai/v1/")
    assert requests[0].url == httpx.URL("https://bedrock-mantle.us-east-1.api.aws/openai/v1/models")
    assert requests[0].headers["Authorization"] == "Bearer bedrock token"


@pytest.mark.asyncio
async def test_async_provider_owns_endpoint_and_bearer_authentication() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, request=request, json={})

    client = AsyncOpenAI(
        provider=bedrock(region="us-east-1", token_provider=lambda: "bedrock token"),
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler), trust_env=False),
    )
    await client.get("/models", cast_to=httpx.Response)
    await client.close()

    assert requests[0].headers["Authorization"] == "Bearer bedrock token"


def test_provider_ignores_openai_environment_configuration() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, request=request, json={})

    with update_env(
        OPENAI_API_KEY="openai token",
        OPENAI_BASE_URL="https://api.openai.invalid/v1",
        OPENAI_CUSTOM_HEADERS="Authorization: Bearer openai custom token",
    ):
        client = OpenAI(
            provider=bedrock(region="us-east-1", api_key="bedrock token"),
            http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
        )
        client.get("/models", cast_to=httpx.Response)

    assert client.api_key == ""
    assert requests[0].url.host == "bedrock-mantle.us-east-1.api.aws"
    assert requests[0].headers["Authorization"] == "Bearer bedrock token"


@pytest.mark.parametrize(
    ("option", "value"),
    [
        ("api_key", "openai token"),
        ("admin_api_key", "admin token"),
        ("workload_identity", cast(Any, object())),
        ("base_url", "https://api.openai.invalid/v1"),
    ],
)
def test_provider_rejects_top_level_authentication_and_routing(option: str, value: object) -> None:
    with pytest.raises(
        OpenAIError,
        match=rf"`provider` cannot be combined with top-level `{option}`.*`bedrock\(\.\.\.\)`",
    ):
        OpenAI(provider=bedrock(region="us-east-1", api_key="bedrock token"), **{option: value})  # type: ignore[arg-type]


def test_provider_survives_with_options_and_can_be_replaced() -> None:
    client = OpenAI(provider=bedrock(region="us-east-1", api_key="first"))

    copied = client.with_options(timeout=1)
    replaced = client.with_options(provider=bedrock(region="eu-west-1", api_key="second"))

    assert copied.base_url == client.base_url
    assert copied._provider is client._provider
    assert replaced.base_url == httpx.URL("https://bedrock-mantle.eu-west-1.api.aws/openai/v1/")
    assert replaced._provider is not client._provider


def test_switching_to_provider_drops_inherited_openai_metadata() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, request=request, json={})

    with update_env(
        OPENAI_CUSTOM_HEADERS="X-OpenAI-Ambient: leak",
        OPENAI_ORG_ID="ambient-org",
        OPENAI_PROJECT_ID="ambient-project",
    ):
        client = OpenAI(
            api_key="openai token",
            default_headers={"X-OpenAI-Custom": "leak"},
            http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
        )
        provider_client = client.with_options(provider=bedrock(region="us-east-1", api_key="bedrock token"))

    provider_client.get("/models", cast_to=httpx.Response)

    headers = requests[0].headers
    assert headers["Authorization"] == "Bearer bedrock token"
    assert "X-OpenAI-Ambient" not in headers
    assert "X-OpenAI-Custom" not in headers
    assert "OpenAI-Organization" not in headers
    assert "OpenAI-Project" not in headers


@pytest.mark.asyncio
async def test_async_switching_to_provider_drops_inherited_openai_metadata() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, request=request, json={})

    client = AsyncOpenAI(
        api_key="openai token",
        organization="openai-org",
        project="openai-project",
        default_headers={"X-OpenAI-Custom": "leak"},
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler), trust_env=False),
    )
    provider_client = client.with_options(provider=bedrock(region="us-east-1", api_key="bedrock token"))

    await provider_client.get("/models", cast_to=httpx.Response)
    await provider_client.close()

    headers = requests[0].headers
    assert headers["Authorization"] == "Bearer bedrock token"
    assert "X-OpenAI-Custom" not in headers
    assert "OpenAI-Organization" not in headers
    assert "OpenAI-Project" not in headers


def test_provider_metadata_survives_same_provider_clone_but_not_replacement() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, request=request, json={})

    first_provider = bedrock(region="us-east-1", api_key="first token")
    client = OpenAI(
        provider=first_provider,
        organization="provider-org",
        project="provider-project",
        default_headers={"X-Provider-Custom": "preserve-me"},
        http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
    )

    client.with_options(timeout=1).get("/models", cast_to=httpx.Response)
    client.with_options(provider=bedrock(region="us-east-1", api_key="second token")).get(
        "/models", cast_to=httpx.Response
    )

    same_provider_headers, replacement_headers = (request.headers for request in requests)
    assert same_provider_headers["X-Provider-Custom"] == "preserve-me"
    assert same_provider_headers["OpenAI-Organization"] == "provider-org"
    assert same_provider_headers["OpenAI-Project"] == "provider-project"
    assert "X-Provider-Custom" not in replacement_headers
    assert "OpenAI-Organization" not in replacement_headers
    assert "OpenAI-Project" not in replacement_headers


def test_provider_normalizes_responses_before_status_handling() -> None:
    class NormalizingProvider:
        name = "normalizing"

        def configure(self) -> _ProviderRuntime:
            def normalize(response: httpx.Response) -> httpx.Response:
                return httpx.Response(200, request=response.request, json={"normalized": True})

            return _ProviderRuntime(
                name=self.name,
                base_url="https://provider.example/v1",
                normalize_response=normalize,
            )

    client = OpenAI(
        provider=_create_provider(NormalizingProvider()),
        max_retries=0,
        http_client=httpx.Client(
            transport=httpx.MockTransport(lambda request: httpx.Response(500, request=request, json={})),
            trust_env=False,
        ),
    )

    response = client.get("/models", cast_to=httpx.Response)

    assert response.status_code == 200
    assert response.json() == {"normalized": True}


def test_environment_bearer_mode_survives_clone_and_refreshes_each_attempt() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, request=request, json={})

    with update_env(AWS_BEARER_TOKEN_BEDROCK="first token"):
        client = OpenAI(
            provider=bedrock(region="us-east-1"),
            http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
        )
        client.get("/models", cast_to=httpx.Response)

    copied = client.with_options(timeout=1)
    with update_env(AWS_BEARER_TOKEN_BEDROCK="second token"):
        copied.get("/models", cast_to=httpx.Response)

    assert [request.headers["Authorization"] for request in requests] == ["Bearer first token", "Bearer second token"]


def test_provider_can_be_removed_with_explicit_openai_credentials() -> None:
    with update_env(OPENAI_CUSTOM_HEADERS=Omit(), OPENAI_ORG_ID=Omit(), OPENAI_PROJECT_ID=Omit()):
        client = OpenAI(
            provider=bedrock(region="us-east-1", api_key="bedrock token"),
            organization="provider-org",
            project="provider-project",
            default_headers={"X-Provider-Custom": "provider value"},
        )

        copied = client.with_options(provider=None, api_key="openai token")

    assert copied._provider is None
    assert copied.api_key == "openai token"
    assert copied.base_url == httpx.URL("https://api.openai.com/v1/")
    assert copied.organization is None
    assert copied.project is None
    assert "X-Provider-Custom" not in copied.default_headers


def test_bearer_provider_does_not_load_botocore(monkeypatch: pytest.MonkeyPatch) -> None:
    def load_botocore() -> None:
        raise AssertionError("bearer authentication must not import botocore")

    monkeypatch.setattr(bedrock_auth_module, "_load_botocore", load_botocore)

    client = OpenAI(provider=bedrock(region="us-east-1", api_key="bedrock token"))
    request = client._build_request(client._prepare_options(_get_options()))
    client._prepare_request(request)

    assert request.headers["Authorization"] == "Bearer bedrock token"


def test_missing_aws_dependency_is_actionable_and_lazy(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__
    network_calls = 0

    def import_module(
        name: str,
        globals: dict[str, Any] | None = None,
        locals: dict[str, Any] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> Any:
        if name.startswith("botocore"):
            raise ImportError(name)
        return real_import(name, globals, locals, fromlist, level)

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal network_calls
        network_calls += 1
        return httpx.Response(200, request=request)

    monkeypatch.setattr(builtins, "__import__", import_module)
    client = OpenAI(
        provider=bedrock(region="us-east-1"),
        http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
    )

    with pytest.raises(OpenAIError, match=r"pip install openai\[bedrock\]"):
        client.get("/models", cast_to=httpx.Response)

    assert network_calls == 0


def test_api_key_none_skips_environment_bearer_fallback() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, request=request, json={})

    with update_env(
        AWS_BEARER_TOKEN_BEDROCK="environment bearer",
        AWS_ACCESS_KEY_ID="access key",
        AWS_SECRET_ACCESS_KEY="secret key",
    ):
        client = OpenAI(
            provider=bedrock(region="us-east-1", api_key=None),
            http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
        )
        client.get("/models", cast_to=httpx.Response)

    assert requests[0].headers["Authorization"].startswith("AWS4-HMAC-SHA256 Credential=access key/")


def test_provider_rejects_custom_authorization_before_network() -> None:
    network_calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal network_calls
        network_calls += 1
        return httpx.Response(200, request=request)

    client = OpenAI(
        provider=bedrock(region="us-east-1", api_key="bedrock token"),
        http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
    )

    with pytest.raises(OpenAIError, match="cannot be combined with a custom `Authorization` header"):
        client.get(
            "/models",
            cast_to=httpx.Response,
            options={"headers": {"Authorization": "Bearer custom"}},
        )

    assert network_calls == 0


def test_bearer_provider_rejects_cross_origin_requests_before_resolving_credentials() -> None:
    network_calls = 0
    provider_calls = 0

    def token_provider() -> str:
        nonlocal provider_calls
        provider_calls += 1
        return "bedrock token"

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal network_calls
        network_calls += 1
        return httpx.Response(200, request=request)

    client = OpenAI(
        provider=bedrock(base_url="https://bedrock.example/openai/v1", token_provider=token_provider),
        http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
    )

    with pytest.raises(OpenAIError, match="origin other than the configured provider URL"):
        client.get("https://attacker.example/steal", cast_to=httpx.Response)

    assert (provider_calls, network_calls) == (0, 0)


@pytest.mark.asyncio
async def test_async_bearer_provider_rejects_cross_origin_requests_before_resolving_credentials() -> None:
    network_calls = 0
    provider_calls = 0

    async def token_provider() -> str:
        nonlocal provider_calls
        provider_calls += 1
        return "bedrock token"

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal network_calls
        network_calls += 1
        return httpx.Response(200, request=request)

    client = AsyncOpenAI(
        provider=bedrock(base_url="https://bedrock.example/openai/v1", token_provider=token_provider),
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler), trust_env=False),
    )

    with pytest.raises(OpenAIError, match="origin other than the configured provider URL"):
        await client.get("https://attacker.example/steal", cast_to=httpx.Response)

    await client.close()
    assert (provider_calls, network_calls) == (0, 0)


def test_bearer_provider_allows_one_shot_body_when_retries_are_disabled() -> None:
    requests: list[httpx.Request] = []

    def body() -> Iterator[bytes]:
        yield b"body"

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, request=request)

    client = OpenAI(
        provider=bedrock(base_url="https://bedrock.example/openai/v1", api_key="bedrock token"),
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
    )

    client.post("/responses", content=body(), cast_to=httpx.Response)

    assert requests[0].content == b"body"


def test_opaque_provider_repr_does_not_expose_credentials() -> None:
    provider = bedrock(
        region="us-east-1",
        access_key_id="secret access key id",
        secret_access_key="secret access key",
        session_token="secret session token",
    )

    assert "secret" not in repr(provider)


def _get_options() -> Any:
    from openai._models import FinalRequestOptions

    return FinalRequestOptions(method="get", url="/models", security={"bearer_auth": True})
