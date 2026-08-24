from __future__ import annotations

from typing import Any, Iterator, cast

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, OpenAIError
from tests.utils import update_env
from openai._types import Omit
from openai.providers import orcarouter


def test_sync_provider_owns_endpoint_and_bearer_authentication() -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={})

    client = OpenAI(
        provider=orcarouter(api_key="orcarouter token"),
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
    )
    client.get("/models", cast_to=httpx2.Response)

    assert client.base_url == httpx2.URL("https://api.orcarouter.ai/v1/")
    assert requests[0].url == httpx2.URL("https://api.orcarouter.ai/v1/models")
    assert requests[0].headers["Authorization"] == "Bearer orcarouter token"


@pytest.mark.asyncio
async def test_async_provider_owns_endpoint_and_bearer_authentication() -> None:
    requests: list[httpx2.Request] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={})

    client = AsyncOpenAI(
        provider=orcarouter(token_provider=lambda: "orcarouter token"),
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False),
    )
    await client.get("/models", cast_to=httpx2.Response)
    await client.close()

    assert requests[0].headers["Authorization"] == "Bearer orcarouter token"


def test_provider_ignores_openai_environment_configuration() -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={})

    with update_env(
        OPENAI_API_KEY="openai token",
        OPENAI_BASE_URL="https://api.openai.invalid/v1",
        OPENAI_CUSTOM_HEADERS="Authorization: Bearer openai custom token",
    ):
        client = OpenAI(
            provider=orcarouter(api_key="orcarouter token"),
            http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
        )
        client.get("/models", cast_to=httpx2.Response)

    assert client.api_key == ""
    assert requests[0].url.host == "api.orcarouter.ai"
    assert requests[0].headers["Authorization"] == "Bearer orcarouter token"


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
        match=rf"`provider` cannot be combined with top-level `{option}`.*`orcarouter\(\.\.\.\)`",
    ):
        OpenAI(provider=orcarouter(api_key="orcarouter token"), **{option: value})  # type: ignore[arg-type]


def test_provider_survives_with_options_and_can_be_replaced() -> None:
    client = OpenAI(provider=orcarouter(api_key="first"))

    copied = client.with_options(timeout=1)
    replaced = client.with_options(provider=orcarouter(api_key="second"))

    assert copied.base_url == client.base_url
    assert copied._provider is client._provider
    assert replaced.base_url == httpx2.URL("https://api.orcarouter.ai/v1/")
    assert replaced._provider is not client._provider


def test_switching_to_provider_drops_inherited_openai_metadata() -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={})

    with update_env(
        OPENAI_CUSTOM_HEADERS="X-OpenAI-Ambient: leak",
        OPENAI_ORG_ID="ambient-org",
        OPENAI_PROJECT_ID="ambient-project",
    ):
        client = OpenAI(
            api_key="openai token",
            default_headers={"X-OpenAI-Custom": "leak"},
            http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
        )
        provider_client = client.with_options(provider=orcarouter(api_key="orcarouter token"))

    provider_client.get("/models", cast_to=httpx2.Response)

    headers = requests[0].headers
    assert headers["Authorization"] == "Bearer orcarouter token"
    assert "X-OpenAI-Ambient" not in headers
    assert "X-OpenAI-Custom" not in headers
    assert "OpenAI-Organization" not in headers
    assert "OpenAI-Project" not in headers


@pytest.mark.asyncio
async def test_async_switching_to_provider_drops_inherited_openai_metadata() -> None:
    requests: list[httpx2.Request] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={})

    client = AsyncOpenAI(
        api_key="openai token",
        organization="openai-org",
        project="openai-project",
        default_headers={"X-OpenAI-Custom": "leak"},
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False),
    )
    provider_client = client.with_options(provider=orcarouter(api_key="orcarouter token"))

    await provider_client.get("/models", cast_to=httpx2.Response)
    await provider_client.close()

    headers = requests[0].headers
    assert headers["Authorization"] == "Bearer orcarouter token"
    assert "X-OpenAI-Custom" not in headers
    assert "OpenAI-Organization" not in headers
    assert "OpenAI-Project" not in headers


def test_provider_metadata_survives_same_provider_clone_but_not_replacement() -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={})

    first_provider = orcarouter(api_key="first token")
    client = OpenAI(
        provider=first_provider,
        organization="provider-org",
        project="provider-project",
        default_headers={"X-Provider-Custom": "preserve-me"},
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
    )

    client.with_options(timeout=1).get("/models", cast_to=httpx2.Response)
    client.with_options(provider=orcarouter(api_key="second token")).get("/models", cast_to=httpx2.Response)

    same_provider_headers, replacement_headers = (request.headers for request in requests)
    assert same_provider_headers["X-Provider-Custom"] == "preserve-me"
    assert same_provider_headers["OpenAI-Organization"] == "provider-org"
    assert same_provider_headers["OpenAI-Project"] == "provider-project"
    assert "X-Provider-Custom" not in replacement_headers
    assert "OpenAI-Organization" not in replacement_headers
    assert "OpenAI-Project" not in replacement_headers


def test_environment_api_key_mode_survives_clone_and_refreshes_each_attempt() -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={})

    with update_env(ORCAROUTER_API_KEY="first token"):
        client = OpenAI(
            provider=orcarouter(),
            http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
        )
        client.get("/models", cast_to=httpx2.Response)

    copied = client.with_options(timeout=1)
    with update_env(ORCAROUTER_API_KEY="second token"):
        copied.get("/models", cast_to=httpx2.Response)

    assert [request.headers["Authorization"] for request in requests] == ["Bearer first token", "Bearer second token"]


def test_provider_can_be_removed_with_explicit_openai_credentials() -> None:
    with update_env(OPENAI_CUSTOM_HEADERS=Omit(), OPENAI_ORG_ID=Omit(), OPENAI_PROJECT_ID=Omit()):
        client = OpenAI(
            provider=orcarouter(api_key="orcarouter token"),
            organization="provider-org",
            project="provider-project",
            default_headers={"X-Provider-Custom": "provider value"},
        )

        copied = client.with_options(provider=None, api_key="openai token")

    assert copied._provider is None
    assert copied.api_key == "openai token"
    assert copied.base_url == httpx2.URL("https://api.openai.com/v1/")
    assert copied.organization is None
    assert copied.project is None
    assert "X-Provider-Custom" not in copied.default_headers


def test_bearer_provider_does_not_require_any_aws_dependency() -> None:
    client = OpenAI(provider=orcarouter(api_key="orcarouter token"))
    request = client._build_request(client._prepare_options(_get_options()))
    client._prepare_request(request)

    assert request.headers["Authorization"] == "Bearer orcarouter token"


def test_explicit_api_key_none_skips_environment_key_and_raises() -> None:
    with update_env(
        ORCAROUTER_API_KEY="environment token",
    ):
        with pytest.raises(OpenAIError, match="ORCAROUTER_API_KEY"):
            OpenAI(provider=orcarouter(api_key=None))


def test_provider_rejects_custom_authorization_before_network() -> None:
    network_calls = 0

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal network_calls
        network_calls += 1
        return httpx2.Response(200, request=request)

    client = OpenAI(
        provider=orcarouter(api_key="orcarouter token"),
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
    )

    with pytest.raises(OpenAIError, match="cannot be combined with a custom `Authorization` header"):
        client.get(
            "/models",
            cast_to=httpx2.Response,
            options={"headers": {"Authorization": "Bearer custom"}},
        )

    assert network_calls == 0


def test_bearer_provider_rejects_cross_origin_requests_before_resolving_credentials() -> None:
    network_calls = 0
    provider_calls = 0

    def token_provider() -> str:
        nonlocal provider_calls
        provider_calls += 1
        return "orcarouter token"

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal network_calls
        network_calls += 1
        return httpx2.Response(200, request=request)

    client = OpenAI(
        provider=orcarouter(base_url="https://orcarouter.example/v1", token_provider=token_provider),
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
    )

    with pytest.raises(OpenAIError, match="origin other than the configured provider URL"):
        client.get("https://attacker.example/steal", cast_to=httpx2.Response)

    assert (provider_calls, network_calls) == (0, 0)


@pytest.mark.asyncio
async def test_async_bearer_provider_rejects_cross_origin_requests_before_resolving_credentials() -> None:
    network_calls = 0
    provider_calls = 0

    async def token_provider() -> str:
        nonlocal provider_calls
        provider_calls += 1
        return "orcarouter token"

    async def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal network_calls
        network_calls += 1
        return httpx2.Response(200, request=request)

    client = AsyncOpenAI(
        provider=orcarouter(base_url="https://orcarouter.example/v1", token_provider=token_provider),
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False),
    )

    with pytest.raises(OpenAIError, match="origin other than the configured provider URL"):
        await client.get("https://attacker.example/steal", cast_to=httpx2.Response)

    await client.close()
    assert (provider_calls, network_calls) == (0, 0)


def test_bearer_provider_allows_one_shot_body_when_retries_are_disabled() -> None:
    requests: list[httpx2.Request] = []

    def body() -> Iterator[bytes]:
        yield b"body"

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request)

    client = OpenAI(
        provider=orcarouter(base_url="https://orcarouter.example/v1", api_key="orcarouter token"),
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
    )

    client.post("/responses", content=body(), cast_to=httpx2.Response)

    assert requests[0].content == b"body"


def test_opaque_provider_repr_does_not_expose_credentials() -> None:
    provider = orcarouter(api_key="secret orcarouter key")

    assert "secret" not in repr(provider)


def test_missing_credentials_is_actionable() -> None:
    with update_env(ORCAROUTER_API_KEY=Omit()):
        with pytest.raises(OpenAIError, match="ORCAROUTER_API_KEY"):
            OpenAI(provider=orcarouter())


def _get_options() -> Any:
    from openai._models import FinalRequestOptions

    return FinalRequestOptions(method="get", url="/models", security={"bearer_auth": True})
