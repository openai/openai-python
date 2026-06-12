from __future__ import annotations

import json
from typing import Any, Union, Protocol, cast
from pathlib import Path

import httpx
import pytest
from httpx import URL
from respx import MockRouter

import openai.lib._bedrock_auth as bedrock_auth_module
from openai import OpenAIError, NotFoundError
from tests.utils import update_env
from openai._types import Omit
from openai.lib.bedrock import BedrockOpenAI, AsyncBedrockOpenAI

Client = Union[BedrockOpenAI, AsyncBedrockOpenAI]

RESPONSE_BODY: dict[str, Any] = {
    "id": "resp_123",
    "object": "response",
    "created_at": 0,
    "status": "completed",
    "background": False,
    "error": None,
    "incomplete_details": None,
    "instructions": None,
    "max_output_tokens": None,
    "max_tool_calls": None,
    "model": "gpt-4o",
    "output": [],
    "parallel_tool_calls": True,
    "previous_response_id": None,
    "prompt_cache_key": None,
    "reasoning": {"effort": None, "summary": None},
    "safety_identifier": None,
    "service_tier": "default",
    "store": True,
    "temperature": 1.0,
    "text": {"format": {"type": "text"}, "verbosity": "medium"},
    "tool_choice": "auto",
    "tools": [],
    "top_logprobs": 0,
    "top_p": 1.0,
    "truncation": "disabled",
    "usage": {
        "input_tokens": 0,
        "input_tokens_details": {"cached_tokens": 0},
        "output_tokens": 0,
        "output_tokens_details": {"reasoning_tokens": 0},
        "total_tokens": 0,
    },
    "user": None,
    "metadata": {},
}
COMPACTED_RESPONSE_BODY: dict[str, Any] = {
    "id": "resp_123",
    "created_at": 0,
    "object": "response.compaction",
    "output": [],
    "usage": RESPONSE_BODY["usage"],
}
INPUT_ITEMS_BODY: dict[str, Any] = {
    "object": "list",
    "data": [],
    "first_id": "item_123",
    "last_id": "item_123",
    "has_more": False,
}
INPUT_TOKENS_BODY: dict[str, Any] = {
    "object": "response.input_tokens",
    "input_tokens": 1,
}


class MockRequestCall(Protocol):
    request: httpx.Request


class MockAwsCredentials:
    def __init__(self, access_key: str, secret_key: str, token: str | None = None) -> None:
        self.access_key = access_key
        self.secret_key = secret_key
        self.token = token


def make_sync_client(**kwargs: Any) -> BedrockOpenAI:
    return BedrockOpenAI(http_client=httpx.Client(trust_env=False), **kwargs)


def make_async_client(**kwargs: Any) -> AsyncBedrockOpenAI:
    return AsyncBedrockOpenAI(http_client=httpx.AsyncClient(trust_env=False), **kwargs)


def response_created_sse() -> str:
    event: dict[str, Any] = {"type": "response.created", "sequence_number": 0, "response": RESPONSE_BODY}
    return f"event: response.created\ndata: {json.dumps(event)}\n\n"


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_region_derived_base_url(client_cls: type[Client]) -> None:
    with update_env(AWS_BEDROCK_BASE_URL=Omit(), AWS_REGION="us-east-1", AWS_DEFAULT_REGION=Omit()):
        client = (
            make_sync_client(api_key="token") if client_cls is BedrockOpenAI else make_async_client(api_key="token")
        )

    assert client.base_url == URL("https://bedrock-mantle.us-east-1.api.aws/openai/v1/")


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_bedrock_config_precedence(client_cls: type[Client]) -> None:
    with update_env(
        AWS_BEDROCK_BASE_URL="https://env.example.com/openai/v1",
        AWS_BEARER_TOKEN_BEDROCK="env token",
        AWS_REGION="us-east-1",
        AWS_DEFAULT_REGION="us-west-2",
    ):
        client = (
            make_sync_client(
                base_url="https://explicit.example.com/openai/v1/responses",
                api_key="explicit token",
            )
            if client_cls is BedrockOpenAI
            else make_async_client(
                base_url="https://explicit.example.com/openai/v1/responses",
                api_key="explicit token",
            )
        )

    assert client.base_url == URL("https://explicit.example.com/openai/v1/")
    assert client.api_key == "explicit token"


@pytest.mark.respx()
def test_env_bearer_does_not_require_botocore(monkeypatch: pytest.MonkeyPatch, respx_mock: MockRouter) -> None:
    real_import_module = bedrock_auth_module.importlib.import_module

    def import_module(name: str) -> Any:
        if name.startswith("botocore"):
            raise ImportError(name)
        return real_import_module(name)

    monkeypatch.setattr(bedrock_auth_module.importlib, "import_module", import_module)
    respx_mock.post("https://example.com/openai/v1/responses").mock(
        return_value=httpx.Response(200, json=RESPONSE_BODY)
    )
    with update_env(
        AWS_BEDROCK_BASE_URL="https://example.com/openai/v1",
        AWS_BEARER_TOKEN_BEDROCK="env token",
    ):
        client = make_sync_client()

    client.responses.create(model="gpt-4o", input="hello")

    request = cast("list[MockRequestCall]", respx_mock.calls)[0].request
    assert request.headers["Authorization"] == "Bearer env token"


def test_empty_env_bearer_without_botocore_uses_aws_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import_module = bedrock_auth_module.importlib.import_module

    def import_module(name: str) -> Any:
        if name.startswith("botocore"):
            raise ImportError(name)
        return real_import_module(name)

    monkeypatch.setattr(bedrock_auth_module.importlib, "import_module", import_module)
    with update_env(AWS_BEARER_TOKEN_BEDROCK="", AWS_REGION="us-east-1"):
        client = make_sync_client()
        with pytest.raises(OpenAIError, match="requires optional AWS dependencies"):
            client.get("/models", cast_to=httpx.Response)


@pytest.mark.respx()
def test_env_bearer_does_not_use_botocore_bearer_auth(monkeypatch: pytest.MonkeyPatch, respx_mock: MockRouter) -> None:
    auth_module = bedrock_auth_module.importlib.import_module("botocore.auth")
    calls = 0
    real_add_auth = auth_module.BearerAuth.add_auth

    def add_auth(auth: object, request: object) -> None:
        nonlocal calls
        calls += 1
        real_add_auth(auth, request)

    monkeypatch.setattr(auth_module.BearerAuth, "add_auth", add_auth)
    respx_mock.post("https://example.com/openai/v1/responses").mock(
        return_value=httpx.Response(200, json=RESPONSE_BODY)
    )
    with update_env(AWS_BEARER_TOKEN_BEDROCK="env token"):
        client = make_sync_client(base_url="https://example.com/openai/v1")

    client.responses.create(model="gpt-4o", input="hello")

    request = cast("list[MockRequestCall]", respx_mock.calls)[0].request
    assert request.headers["Authorization"] == "Bearer env token"
    assert calls == 0


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_empty_env_bearer_falls_back_to_aws_credentials(client_cls: type[Client]) -> None:
    with update_env(AWS_BEARER_TOKEN_BEDROCK="", AWS_REGION="us-east-1"):
        client = make_sync_client() if client_cls is BedrockOpenAI else make_async_client()

    assert client.api_key == ""
    assert client._uses_aws_auth()


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_bedrock_region_precedence(client_cls: type[Client]) -> None:
    with update_env(AWS_BEDROCK_BASE_URL=Omit(), AWS_REGION="us-east-1", AWS_DEFAULT_REGION="us-west-2"):
        explicit_region_client = (
            make_sync_client(aws_region="eu-west-1", api_key="token")
            if client_cls is BedrockOpenAI
            else make_async_client(aws_region="eu-west-1", api_key="token")
        )
        aws_region_client = (
            make_sync_client(api_key="token") if client_cls is BedrockOpenAI else make_async_client(api_key="token")
        )

    with update_env(AWS_BEDROCK_BASE_URL=Omit(), AWS_REGION=Omit(), AWS_DEFAULT_REGION="us-west-2"):
        default_region_client = (
            make_sync_client(api_key="token") if client_cls is BedrockOpenAI else make_async_client(api_key="token")
        )

    assert explicit_region_client.base_url == URL("https://bedrock-mantle.eu-west-1.api.aws/openai/v1/")
    assert aws_region_client.base_url == URL("https://bedrock-mantle.us-east-1.api.aws/openai/v1/")
    assert default_region_client.base_url == URL("https://bedrock-mantle.us-west-2.api.aws/openai/v1/")


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_aws_profile_supplies_region(client_cls: type[Client], tmp_path: Path) -> None:
    config_path = tmp_path / "config"
    config_path.write_text("[profile production]\nregion = eu-central-1\n")
    with update_env(
        AWS_CONFIG_FILE=str(config_path),
        AWS_BEDROCK_BASE_URL=Omit(),
        AWS_REGION=Omit(),
        AWS_DEFAULT_REGION=Omit(),
    ):
        client = (
            make_sync_client(aws_profile="production")
            if client_cls is BedrockOpenAI
            else make_async_client(aws_profile="production")
        )

    assert client.aws_region == "eu-central-1"
    assert client.base_url == URL("https://bedrock-mantle.eu-central-1.api.aws/openai/v1/")


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_normalizes_responses_url(client_cls: type[Client]) -> None:
    client = (
        make_sync_client(base_url="https://example.com/openai/v1/responses", api_key="token")
        if client_cls is BedrockOpenAI
        else make_async_client(base_url="https://example.com/openai/v1/responses", api_key="token")
    )

    assert client.base_url == URL("https://example.com/openai/v1/")


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_requires_endpoint_configuration(client_cls: type[Client]) -> None:
    with update_env(AWS_BEDROCK_BASE_URL=Omit(), AWS_REGION=Omit(), AWS_DEFAULT_REGION=Omit()):
        with pytest.raises(OpenAIError, match="Bedrock requires an AWS region"):
            client_cls(api_key="token")


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_does_not_use_openai_api_key(client_cls: type[Client]) -> None:
    with update_env(
        OPENAI_API_KEY="openai token",
        AWS_BEARER_TOKEN_BEDROCK=Omit(),
        AWS_BEDROCK_BASE_URL="https://example.com/openai/v1",
        AWS_REGION="us-east-1",
    ):
        client = make_sync_client() if client_cls is BedrockOpenAI else make_async_client()

    assert client.api_key == ""
    assert client._uses_aws_auth()


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_rejects_static_token_and_provider(client_cls: type[Client]) -> None:
    with pytest.raises(OpenAIError, match="authentication is ambiguous"):
        client_cls(
            base_url="https://example.com/openai/v1",
            api_key="token",
            bedrock_token_provider=lambda: "provider token",
        )


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_rejects_empty_explicit_bearer_token(client_cls: type[Client]) -> None:
    with pytest.raises(OpenAIError, match="must not be empty"):
        client_cls(base_url="https://example.com/openai/v1", api_key="")


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_rejects_bearer_and_aws_credentials(client_cls: type[Client]) -> None:
    with pytest.raises(OpenAIError, match="authentication is ambiguous"):
        client_cls(
            base_url="https://example.com/openai/v1",
            api_key="token",
            aws_access_key_id="access key",
            aws_secret_access_key="secret key",
        )


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_rejects_partial_explicit_aws_credentials(client_cls: type[Client]) -> None:
    with pytest.raises(OpenAIError, match="require both"):
        client_cls(
            base_url="https://example.com/openai/v1",
            aws_region="us-east-1",
            aws_access_key_id="access key",
        )


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_requires_refreshable_tokens_to_use_provider_option(client_cls: type[Client]) -> None:
    with pytest.raises(OpenAIError, match="bedrock_token_provider"):
        client_cls(
            base_url="https://example.com/openai/v1",
            api_key=lambda: "provider token",  # type: ignore[arg-type]
        )


@pytest.mark.respx()
def test_token_provider_refresh_sync(respx_mock: MockRouter) -> None:
    respx_mock.post("https://example.com/openai/v1/responses").mock(
        side_effect=[
            httpx.Response(500, json={"error": "server error"}),
            httpx.Response(200, json=RESPONSE_BODY),
        ]
    )
    tokens = iter(["first", "second"])
    client = BedrockOpenAI(
        base_url="https://example.com/openai/v1",
        bedrock_token_provider=lambda: next(tokens),
        http_client=httpx.Client(trust_env=False),
        max_retries=1,
    )

    client.responses.create(model="gpt-4o", input="hello")

    calls = cast("list[MockRequestCall]", respx_mock.calls)
    assert calls[0].request.headers["Authorization"] == "Bearer first"
    assert calls[1].request.headers["Authorization"] == "Bearer second"


@pytest.mark.asyncio
@pytest.mark.respx()
async def test_token_provider_refresh_async(respx_mock: MockRouter) -> None:
    respx_mock.post("https://example.com/openai/v1/responses").mock(
        side_effect=[
            httpx.Response(500, json={"error": "server error"}),
            httpx.Response(200, json=RESPONSE_BODY),
        ]
    )
    tokens = iter(["first", "second"])
    client = AsyncBedrockOpenAI(
        base_url="https://example.com/openai/v1",
        bedrock_token_provider=lambda: next(tokens),
        http_client=httpx.AsyncClient(trust_env=False),
        max_retries=1,
    )

    await client.responses.create(model="gpt-4o", input="hello")

    calls = cast("list[MockRequestCall]", respx_mock.calls)
    assert calls[0].request.headers["Authorization"] == "Bearer first"
    assert calls[1].request.headers["Authorization"] == "Bearer second"


@pytest.mark.respx()
def test_explicit_aws_credentials_override_ambient_bearer(respx_mock: MockRouter) -> None:
    respx_mock.post("https://example.com/openai/v1/responses").mock(
        return_value=httpx.Response(200, json=RESPONSE_BODY)
    )
    with update_env(AWS_BEARER_TOKEN_BEDROCK="ambient token"):
        client = BedrockOpenAI(
            base_url="https://example.com/openai/v1",
            aws_region="us-east-1",
            aws_access_key_id="access key",
            aws_secret_access_key="secret key",
            aws_session_token="session token",
            http_client=httpx.Client(trust_env=False),
        )

    client.responses.create(model="gpt-4o", input="hello")

    request = cast("list[MockRequestCall]", respx_mock.calls)[0].request
    assert request.headers["Authorization"].startswith("AWS4-HMAC-SHA256 Credential=access key/")
    assert request.headers["X-Amz-Security-Token"] == "session token"


@pytest.mark.respx()
def test_aws_credentials_provider_refreshes_before_retries(respx_mock: MockRouter) -> None:
    respx_mock.post("https://example.com/openai/v1/responses").mock(
        side_effect=[
            httpx.Response(500, json={"error": "server error"}),
            httpx.Response(200, json=RESPONSE_BODY),
        ]
    )
    credentials = iter(
        [
            MockAwsCredentials("first access key", "first secret", "first session token"),
            MockAwsCredentials("second access key", "second secret", "second session token"),
        ]
    )
    client = BedrockOpenAI(
        base_url="https://example.com/openai/v1",
        aws_region="us-east-1",
        aws_credentials_provider=lambda: next(credentials),
        http_client=httpx.Client(trust_env=False),
        max_retries=1,
    )

    client.responses.create(model="gpt-4o", input="hello")

    calls = cast("list[MockRequestCall]", respx_mock.calls)
    assert "Credential=first access key/" in calls[0].request.headers["Authorization"]
    assert calls[0].request.headers["X-Amz-Security-Token"] == "first session token"
    assert "Credential=second access key/" in calls[1].request.headers["Authorization"]
    assert calls[1].request.headers["X-Amz-Security-Token"] == "second session token"


def test_preserves_token_provider_across_with_options() -> None:
    client = BedrockOpenAI(
        base_url="https://example.com/openai/v1",
        bedrock_token_provider=lambda: "provider token",
        http_client=httpx.Client(trust_env=False),
    )

    copied_client = client.with_options(timeout=1)

    assert copied_client._refresh_api_key() == "provider token"


def test_preserves_environment_bearer_across_with_options() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, request=request, json={})

    with update_env(AWS_BEARER_TOKEN_BEDROCK="first token"):
        client = BedrockOpenAI(
            base_url="https://example.com/openai/v1",
            http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
        )

    with update_env(AWS_BEARER_TOKEN_BEDROCK="second token"):
        copied_client = client.with_options(timeout=1)
        copied_client.get("/models", cast_to=httpx.Response)

    assert copied_client.api_key == "first token"
    assert requests[0].headers["Authorization"] == "Bearer first token"


def test_environment_bearer_routing_copy_remains_mutable() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, request=request, json={})

    with update_env(AWS_BEARER_TOKEN_BEDROCK="first token"):
        client = BedrockOpenAI(
            aws_region="us-east-1",
            http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
        )
    copied_client = client.with_options(aws_region="us-west-2")
    copied_client.api_key = "second token"
    copied_client.get("/models", cast_to=httpx.Response)

    assert copied_client.api_key == "second token"
    assert requests[0].headers["Authorization"] == "Bearer second token"


def test_legacy_api_key_mutation_updates_requests_and_copies() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, request=request, json={})

    client = BedrockOpenAI(
        base_url="https://example.com/openai/v1",
        api_key="first token",
        http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
    )
    client.api_key = "second token"
    client.get("/models", cast_to=httpx.Response)
    copied_client = client.with_options(timeout=1)
    copied_client.get("/models", cast_to=httpx.Response)
    client.api_key = "first token"
    reverted_client = client.with_options(timeout=2)
    reverted_client.get("/models", cast_to=httpx.Response)

    assert copied_client.api_key == "second token"
    assert reverted_client.api_key == "first token"
    assert [request.headers["Authorization"] for request in requests] == [
        "Bearer second token",
        "Bearer second token",
        "Bearer first token",
    ]


def test_legacy_api_key_mutation_switches_aws_client_to_bearer() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, request=request, json={})

    client = BedrockOpenAI(
        base_url="https://example.com/openai/v1",
        aws_region="us-east-1",
        aws_access_key_id="access key",
        aws_secret_access_key="secret key",
        http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
    )
    client.api_key = "bearer token"
    client.get("/models", cast_to=httpx.Response, options={"follow_redirects": True})

    assert requests[0].headers["Authorization"] == "Bearer bearer token"


def test_explicit_aws_copy_override_wins_over_mutated_api_key() -> None:
    client = BedrockOpenAI(
        base_url="https://example.com/openai/v1",
        api_key="first token",
        http_client=httpx.Client(trust_env=False),
    )
    client.api_key = "second token"

    copied_client = client.with_options(
        aws_region="us-east-1",
        aws_access_key_id="access key",
        aws_secret_access_key="secret key",
    )

    assert copied_client._uses_aws_auth()
    assert copied_client.api_key == ""


def test_clearing_legacy_bearer_does_not_switch_to_aws_authentication() -> None:
    network_calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal network_calls
        network_calls += 1
        return httpx.Response(200, request=request)

    with update_env(AWS_ACCESS_KEY_ID="access key", AWS_SECRET_ACCESS_KEY="secret key"):
        client = BedrockOpenAI(
            base_url="https://example.com/openai/v1",
            api_key="bearer token",
            http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
        )
        client.api_key = None  # type: ignore[assignment]
        with pytest.raises(OpenAIError, match="bearer credential must not be empty"):
            client.get("/models", cast_to=httpx.Response)

    assert network_calls == 0


def test_legacy_state_repr_does_not_expose_credentials() -> None:
    client = BedrockOpenAI(
        base_url="https://example.com/openai/v1",
        aws_region="us-east-1",
        aws_access_key_id="secret access key id",
        aws_secret_access_key="secret access key",
        aws_session_token="secret session token",
        http_client=httpx.Client(trust_env=False),
    )

    assert "secret" not in repr(client._bedrock_state)

    bearer_client = BedrockOpenAI(
        base_url="https://example.com/openai/v1",
        api_key="secret bearer token",
        http_client=httpx.Client(trust_env=False),
    )
    assert "secret bearer token" not in repr(bearer_client._bedrock_runtime_signature)


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_direct_routing_mutations_survive_clone(client_cls: type[Client]) -> None:
    client = (
        make_sync_client(base_url="https://first.example/openai/v1", aws_region="us-east-1", api_key="token")
        if client_cls is BedrockOpenAI
        else make_async_client(
            base_url="https://first.example/openai/v1",
            aws_region="us-east-1",
            api_key="token",
        )
    )
    client.base_url = "https://second.example/openai/v1"
    client.aws_region = "us-west-2"

    copied_client = client.with_options(timeout=1)

    assert copied_client.base_url == URL("https://second.example/openai/v1/")
    assert copied_client.aws_region == "us-west-2"
    assert not copied_client._bedrock_state.uses_region_derived_base_url


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_direct_region_mutation_survives_clone(client_cls: type[Client]) -> None:
    with update_env(AWS_BEDROCK_BASE_URL=Omit(), AWS_REGION=Omit(), AWS_DEFAULT_REGION=Omit()):
        client = (
            make_sync_client(aws_region="us-east-1", api_key="token")
            if client_cls is BedrockOpenAI
            else make_async_client(aws_region="us-east-1", api_key="token")
        )
        client.aws_region = "us-west-2"
        copied_client = client.with_options(timeout=1)

    assert copied_client.aws_region == "us-west-2"
    assert copied_client.base_url == URL("https://bedrock-mantle.us-west-2.api.aws/openai/v1/")


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_direct_base_url_mutation_survives_auth_override(client_cls: type[Client]) -> None:
    with update_env(AWS_BEDROCK_BASE_URL=Omit(), AWS_REGION=Omit(), AWS_DEFAULT_REGION=Omit()):
        client = (
            make_sync_client(
                aws_region="us-east-1",
                aws_access_key_id="access key",
                aws_secret_access_key="secret key",
            )
            if client_cls is BedrockOpenAI
            else make_async_client(
                aws_region="us-east-1",
                aws_access_key_id="access key",
                aws_secret_access_key="secret key",
            )
        )
        client.base_url = "https://custom.example/openai/v1"
        copied_client = client.with_options(api_key="bearer token")

    assert copied_client.base_url == URL("https://custom.example/openai/v1/")
    assert not copied_client._uses_aws_auth()


def test_preserves_aws_credentials_across_with_options() -> None:
    client = BedrockOpenAI(
        base_url="https://example.com/openai/v1",
        aws_region="us-east-1",
        aws_access_key_id="access key",
        aws_secret_access_key="secret key",
        http_client=httpx.Client(trust_env=False),
    )

    copied_client = client.with_options(timeout=1)

    assert copied_client._uses_aws_auth()
    assert copied_client._bedrock_state.aws_access_key_id == "access key"


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_preserves_default_chain_mode_across_with_options(client_cls: type[Client]) -> None:
    with update_env(AWS_BEARER_TOKEN_BEDROCK=Omit(), AWS_REGION="us-east-1"):
        client = make_sync_client() if client_cls is BedrockOpenAI else make_async_client()

    with update_env(AWS_BEARER_TOKEN_BEDROCK="late bearer", AWS_REGION="us-east-1"):
        copied_client = client.with_options(timeout=1)

    assert copied_client._uses_aws_auth()
    assert copied_client._bedrock_state.aws_profile is None
    assert copied_client._bedrock_state.aws_access_key_id is None
    assert copied_client._bedrock_state.aws_credentials_provider is None
    assert copied_client.api_key == ""


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_preserves_region_derived_url_provenance_across_multiple_copies(client_cls: type[Client]) -> None:
    with update_env(AWS_BEDROCK_BASE_URL=Omit(), AWS_REGION=Omit(), AWS_DEFAULT_REGION=Omit()):
        client = (
            make_sync_client(aws_region="us-east-1", api_key="token")
            if client_cls is BedrockOpenAI
            else make_async_client(aws_region="us-east-1", api_key="token")
        )
        copied_client = client.with_options(timeout=1).with_options(aws_region="eu-west-1")

    assert copied_client.base_url == URL("https://bedrock-mantle.eu-west-1.api.aws/openai/v1/")


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_preserves_region_derived_url_after_auth_override(client_cls: type[Client]) -> None:
    with update_env(AWS_BEDROCK_BASE_URL=Omit(), AWS_REGION=Omit(), AWS_DEFAULT_REGION=Omit()):
        client = (
            make_sync_client(aws_region="us-east-1", api_key="token")
            if client_cls is BedrockOpenAI
            else make_async_client(aws_region="us-east-1", api_key="token")
        )
        copied_client = client.with_options(
            aws_access_key_id="access key",
            aws_secret_access_key="secret key",
        ).with_options(aws_region="us-west-2")

    assert copied_client.base_url == URL("https://bedrock-mantle.us-west-2.api.aws/openai/v1/")


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_blank_base_url_restores_region_derived_url_provenance(client_cls: type[Client]) -> None:
    with update_env(AWS_BEDROCK_BASE_URL=Omit(), AWS_REGION=Omit(), AWS_DEFAULT_REGION=Omit()):
        client = (
            make_sync_client(aws_region="us-east-1", api_key="token")
            if client_cls is BedrockOpenAI
            else make_async_client(aws_region="us-east-1", api_key="token")
        )
        copied_client = client.with_options(base_url="").with_options(aws_region="eu-west-1")

    assert copied_client.base_url == URL("https://bedrock-mantle.eu-west-1.api.aws/openai/v1/")


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_with_options_replaces_the_aws_credential_source(client_cls: type[Client], tmp_path: Path) -> None:
    config_path = tmp_path / "config"
    config_path.write_text("[profile other-profile]\nregion = us-east-1\n")
    explicit_credentials_client = (
        make_sync_client(
            base_url="https://example.com/openai/v1",
            aws_region="us-east-1",
            aws_access_key_id="access key",
            aws_secret_access_key="secret key",
        )
        if client_cls is BedrockOpenAI
        else make_async_client(
            base_url="https://example.com/openai/v1",
            aws_region="us-east-1",
            aws_access_key_id="access key",
            aws_secret_access_key="secret key",
        )
    )
    with update_env(AWS_CONFIG_FILE=str(config_path)):
        profile_client = explicit_credentials_client.with_options(aws_profile="other-profile")

    assert profile_client._bedrock_state.aws_profile == "other-profile"
    assert profile_client._bedrock_state.aws_access_key_id is None
    assert profile_client._bedrock_state.aws_secret_access_key is None

    explicit_credentials_client = profile_client.with_options(
        aws_access_key_id="replacement access key",
        aws_secret_access_key="replacement secret key",
    )

    assert explicit_credentials_client._bedrock_state.aws_profile is None
    assert explicit_credentials_client._bedrock_state.aws_access_key_id == "replacement access key"
    assert explicit_credentials_client._bedrock_state.aws_secret_access_key == "replacement secret key"


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_with_options_replacing_profile_re_resolves_profile_region(client_cls: type[Client], tmp_path: Path) -> None:
    config_path = tmp_path / "config"
    config_path.write_text("[profile east]\nregion = us-east-1\n[profile west]\nregion = us-west-2\n")

    with update_env(
        AWS_CONFIG_FILE=str(config_path),
        AWS_BEARER_TOKEN_BEDROCK=Omit(),
        AWS_BEDROCK_BASE_URL=Omit(),
        AWS_REGION=Omit(),
        AWS_DEFAULT_REGION=Omit(),
    ):
        client = (
            make_sync_client(aws_profile="east")
            if client_cls is BedrockOpenAI
            else make_async_client(aws_profile="east")
        )

    with update_env(
        AWS_CONFIG_FILE=str(config_path),
        AWS_BEARER_TOKEN_BEDROCK=Omit(),
        AWS_BEDROCK_BASE_URL="https://late-environment.example.com/v1",
        AWS_REGION=Omit(),
        AWS_DEFAULT_REGION=Omit(),
    ):
        copied_client = client.with_options(aws_profile="west")

    assert copied_client.aws_region == "us-west-2"
    assert copied_client.base_url == URL("https://bedrock-mantle.us-west-2.api.aws/openai/v1/")
    assert copied_client._bedrock_state.aws_profile == "west"


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
@pytest.mark.parametrize(
    ("copy_kwargs", "uses_aws_auth"),
    [
        ({"api_key": "bearer token"}, False),
        (
            {
                "aws_access_key_id": "access key",
                "aws_secret_access_key": "secret key",
            },
            True,
        ),
    ],
)
def test_profile_derived_region_survives_auth_override(
    client_cls: type[Client],
    copy_kwargs: dict[str, Any],
    uses_aws_auth: bool,
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config"
    config_path.write_text("[profile west]\nregion = us-west-2\n")

    with update_env(
        AWS_CONFIG_FILE=str(config_path),
        AWS_BEARER_TOKEN_BEDROCK=Omit(),
        AWS_BEDROCK_BASE_URL=Omit(),
        AWS_REGION=Omit(),
        AWS_DEFAULT_REGION=Omit(),
    ):
        client = (
            make_sync_client(aws_profile="west")
            if client_cls is BedrockOpenAI
            else make_async_client(aws_profile="west")
        )
        copied_client = client.with_options(**copy_kwargs)

    assert copied_client.aws_region == "us-west-2"
    assert copied_client.base_url == URL("https://bedrock-mantle.us-west-2.api.aws/openai/v1/")
    assert copied_client._uses_aws_auth() is uses_aws_auth


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_with_options_switching_from_bearer_to_profile_re_resolves_environment_region(
    client_cls: type[Client], tmp_path: Path
) -> None:
    config_path = tmp_path / "config"
    config_path.write_text("[profile west]\nregion = us-west-2\n")

    with update_env(
        AWS_CONFIG_FILE=str(config_path),
        AWS_BEDROCK_BASE_URL=Omit(),
        AWS_REGION="us-east-1",
        AWS_DEFAULT_REGION=Omit(),
    ):
        client = (
            make_sync_client(api_key="token") if client_cls is BedrockOpenAI else make_async_client(api_key="token")
        )

    with update_env(
        AWS_CONFIG_FILE=str(config_path),
        AWS_BEARER_TOKEN_BEDROCK=Omit(),
        AWS_BEDROCK_BASE_URL=Omit(),
        AWS_REGION=Omit(),
        AWS_DEFAULT_REGION=Omit(),
    ):
        copied_client = client.with_options(aws_profile="west")

    assert copied_client.aws_region == "us-west-2"
    assert copied_client.base_url == URL("https://bedrock-mantle.us-west-2.api.aws/openai/v1/")


def test_with_options_supports_subclasses_with_the_previous_constructor_signature() -> None:
    class LegacyBedrockOpenAI(BedrockOpenAI):
        def __init__(
            self,
            *,
            api_key: str | None = None,
            bedrock_token_provider: Any = None,
            aws_region: str | None = None,
            organization: str | None = None,
            project: str | None = None,
            webhook_secret: str | None = None,
            base_url: str | httpx.URL | None = None,
            websocket_base_url: str | httpx.URL | None = None,
            timeout: Any = None,
            max_retries: int = 2,
            default_headers: Any = None,
            default_query: Any = None,
            http_client: httpx.Client | None = None,
            _enforce_credentials: bool = True,
        ) -> None:
            super().__init__(
                api_key=api_key,
                bedrock_token_provider=bedrock_token_provider,
                aws_region=aws_region,
                organization=organization,
                project=project,
                webhook_secret=webhook_secret,
                base_url=base_url,
                websocket_base_url=websocket_base_url,
                timeout=timeout,
                max_retries=max_retries,
                default_headers=default_headers,
                default_query=default_query,
                http_client=http_client,
                _enforce_credentials=_enforce_credentials,
            )

    client = LegacyBedrockOpenAI(
        api_key="token",
        aws_region="us-east-1",
        http_client=httpx.Client(trust_env=False),
    )

    copied_client = client.with_options(timeout=1).with_options(aws_region="us-west-2")

    assert isinstance(copied_client, LegacyBedrockOpenAI)
    assert copied_client.api_key == "token"
    assert copied_client.base_url == URL("https://bedrock-mantle.us-west-2.api.aws/openai/v1/")


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_with_options_api_key_replaces_token_provider(client_cls: type[Client]) -> None:
    client = (
        make_sync_client(
            base_url="https://example.com/openai/v1",
            bedrock_token_provider=lambda: "provider token",
        )
        if client_cls is BedrockOpenAI
        else make_async_client(
            base_url="https://example.com/openai/v1",
            bedrock_token_provider=lambda: "provider token",
        )
    )

    copied_client = client.with_options(api_key="static token")

    assert copied_client.api_key == "static token"
    assert copied_client._bedrock_token_provider is None


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_with_options_rejects_explicit_bearer_provider_and_aws_credentials(client_cls: type[Client]) -> None:
    client = (
        make_sync_client(base_url="https://example.com/openai/v1", api_key="token")
        if client_cls is BedrockOpenAI
        else make_async_client(base_url="https://example.com/openai/v1", api_key="token")
    )

    with pytest.raises(OpenAIError, match="authentication is ambiguous"):
        client.with_options(
            bedrock_token_provider=lambda: "provider token",
            aws_access_key_id="access key",
            aws_secret_access_key="secret key",
        )


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_with_options_aws_region_recomputes_region_derived_base_url(client_cls: type[Client]) -> None:
    with update_env(AWS_BEDROCK_BASE_URL=Omit(), AWS_REGION=Omit(), AWS_DEFAULT_REGION=Omit()):
        client = (
            make_sync_client(aws_region="us-east-1", api_key="token")
            if client_cls is BedrockOpenAI
            else make_async_client(aws_region="us-east-1", api_key="token")
        )

        copied_client = client.with_options(aws_region="eu-west-1")

    assert copied_client.aws_region == "eu-west-1"
    assert copied_client.base_url == URL("https://bedrock-mantle.eu-west-1.api.aws/openai/v1/")


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_with_options_aws_region_keeps_explicit_base_url(client_cls: type[Client]) -> None:
    client = (
        make_sync_client(base_url="https://example.com/openai/v1", aws_region="us-east-1", api_key="token")
        if client_cls is BedrockOpenAI
        else make_async_client(base_url="https://example.com/openai/v1", aws_region="us-east-1", api_key="token")
    )

    copied_client = client.with_options(aws_region="eu-west-1")

    assert copied_client.aws_region == "eu-west-1"
    assert copied_client.base_url == URL("https://example.com/openai/v1/")


@pytest.mark.parametrize(
    "copy_kwargs",
    [
        {"admin_api_key": "admin token"},
        {"workload_identity": cast(Any, {})},
    ],
)
def test_rejects_non_bedrock_copy_auth(copy_kwargs: dict[str, Any]) -> None:
    client = make_sync_client(base_url="https://example.com/openai/v1", api_key="token")

    with pytest.raises(OpenAIError, match="only supports Bedrock bearer token or AWS credential authentication"):
        client.with_options(**copy_kwargs)


@pytest.mark.respx()
def test_passes_non_responses_resources_through(respx_mock: MockRouter) -> None:
    respx_mock.post("https://example.com/openai/v1/chat/completions").mock(
        return_value=httpx.Response(
            404,
            json={"error": {"message": "AWS does not support chat completions here"}},
            headers={"x-request-id": "req_chat"},
        )
    )
    client = make_sync_client(base_url="https://example.com/openai/v1", api_key="token")

    with pytest.raises(NotFoundError, match="AWS does not support chat completions here") as exc:
        client.chat.completions.create(model="gpt-4o", messages=[])

    assert exc.value.request_id == "req_chat"
    calls = cast("list[MockRequestCall]", respx_mock.calls)
    assert calls[0].request.url == URL("https://example.com/openai/v1/chat/completions")


@pytest.mark.asyncio
@pytest.mark.respx()
async def test_passes_non_responses_resources_through_async(respx_mock: MockRouter) -> None:
    respx_mock.post("https://example.com/openai/v1/chat/completions").mock(
        return_value=httpx.Response(
            404,
            json={"error": {"message": "AWS does not support chat completions here"}},
            headers={"x-request-id": "req_chat"},
        )
    )
    client = make_async_client(base_url="https://example.com/openai/v1", api_key="token")

    with pytest.raises(NotFoundError, match="AWS does not support chat completions here") as exc:
        await client.chat.completions.create(model="gpt-4o", messages=[])

    assert exc.value.request_id == "req_chat"
    calls = cast("list[MockRequestCall]", respx_mock.calls)
    assert calls[0].request.url == URL("https://example.com/openai/v1/chat/completions")


@pytest.mark.respx()
def test_passes_responses_features_through(respx_mock: MockRouter) -> None:
    respx_mock.post("https://example.com/openai/v1/responses").mock(
        return_value=httpx.Response(200, json=RESPONSE_BODY)
    )
    client = make_sync_client(base_url="https://example.com/openai/v1", api_key="token")

    response = client.responses.create(
        model="gpt-4o",
        input="hello",
        tools=[{"type": "web_search_preview"}],  # type: ignore[list-item]
    )

    assert response.id == "resp_123"
    calls = cast("list[MockRequestCall]", respx_mock.calls)
    assert json.loads(calls[0].request.content)["tools"] == [{"type": "web_search_preview"}]


@pytest.mark.respx()
def test_passes_admin_security_routes_through(respx_mock: MockRouter) -> None:
    respx_mock.get("https://example.com/openai/v1/organization/invites").mock(
        return_value=httpx.Response(
            404,
            json={"error": {"message": "AWS does not support organization invites here"}},
            headers={"x-request-id": "req_admin"},
        )
    )
    client = make_sync_client(base_url="https://example.com/openai/v1", api_key="token")

    with pytest.raises(NotFoundError, match="AWS does not support organization invites here"):
        list(client.admin.organization.invites.list())

    calls = cast("list[MockRequestCall]", respx_mock.calls)
    assert calls[0].request.headers["Authorization"] == "Bearer token"


@pytest.mark.respx()
def test_refreshes_token_provider_for_admin_security_routes(respx_mock: MockRouter) -> None:
    respx_mock.get("https://example.com/openai/v1/organization/invites").mock(
        side_effect=[
            httpx.Response(500, json={"error": "server error"}),
            httpx.Response(
                404,
                json={"error": {"message": "AWS does not support organization invites here"}},
                headers={"x-request-id": "req_admin"},
            ),
        ]
    )
    tokens = iter(["first", "second"])
    client = BedrockOpenAI(
        base_url="https://example.com/openai/v1",
        bedrock_token_provider=lambda: next(tokens),
        http_client=httpx.Client(trust_env=False),
        max_retries=1,
    )

    with pytest.raises(NotFoundError, match="AWS does not support organization invites here"):
        list(client.admin.organization.invites.list())

    calls = cast("list[MockRequestCall]", respx_mock.calls)
    assert calls[0].request.headers["Authorization"] == "Bearer first"
    assert calls[1].request.headers["Authorization"] == "Bearer second"


@pytest.mark.respx()
def test_allows_responses_http_methods(respx_mock: MockRouter) -> None:
    respx_mock.post("https://example.com/openai/v1/responses").mock(
        return_value=httpx.Response(200, json=RESPONSE_BODY)
    )
    respx_mock.get("https://example.com/openai/v1/responses/resp_123?starting_after=1&stream=true").mock(
        return_value=httpx.Response(200, text=response_created_sse(), headers={"Content-Type": "text/event-stream"})
    )
    respx_mock.get("https://example.com/openai/v1/responses/resp_123?stream=true").mock(
        return_value=httpx.Response(200, text=response_created_sse(), headers={"Content-Type": "text/event-stream"})
    )
    respx_mock.get("https://example.com/openai/v1/responses/resp_123").mock(
        return_value=httpx.Response(200, json=RESPONSE_BODY)
    )
    respx_mock.post("https://example.com/openai/v1/responses/resp_123/cancel").mock(
        return_value=httpx.Response(200, json=RESPONSE_BODY)
    )
    respx_mock.post("https://example.com/openai/v1/responses/compact").mock(
        return_value=httpx.Response(200, json=COMPACTED_RESPONSE_BODY)
    )
    respx_mock.get("https://example.com/openai/v1/responses/resp_123/input_items").mock(
        return_value=httpx.Response(200, json=INPUT_ITEMS_BODY)
    )
    respx_mock.post("https://example.com/openai/v1/responses/input_tokens").mock(
        return_value=httpx.Response(200, json=INPUT_TOKENS_BODY)
    )
    client = make_sync_client(base_url="https://example.com/openai/v1", api_key="token")

    assert client.responses.create(model="gpt-4o", input="hello", background=True).id == "resp_123"
    assert client.responses.retrieve("resp_123").id == "resp_123"
    assert [event.type for event in client.responses.retrieve("resp_123", starting_after=1, stream=True)] == [
        "response.created"
    ]
    assert [event.type for event in client.responses.retrieve("resp_123", stream=True)] == ["response.created"]
    assert client.responses.cancel("resp_123").id == "resp_123"
    assert client.responses.compact(model="gpt-4o").object == "response.compaction"
    assert list(client.responses.input_items.list("resp_123")) == []
    assert client.responses.input_tokens.count(model="gpt-4o", input="hello").input_tokens == 1

    calls = cast("list[MockRequestCall]", respx_mock.calls)
    assert {call.request.headers["Authorization"] for call in calls} == {"Bearer token"}


@pytest.mark.respx()
def test_allows_sse_and_response_wrappers(respx_mock: MockRouter) -> None:
    respx_mock.post("https://example.com/openai/v1/responses").mock(
        side_effect=[
            httpx.Response(200, text=response_created_sse(), headers={"Content-Type": "text/event-stream"}),
            httpx.Response(200, json=RESPONSE_BODY),
            httpx.Response(200, json=RESPONSE_BODY),
        ]
    )
    client = make_sync_client(base_url="https://example.com/openai/v1", api_key="token")

    events = list(client.responses.create(model="gpt-4o", input="hello", stream=True))
    assert [event.type for event in events] == ["response.created"]

    raw_response = client.responses.with_raw_response.create(model="gpt-4o", input="hello")
    assert raw_response.parse().id == "resp_123"

    with client.responses.with_streaming_response.create(model="gpt-4o", input="hello") as response:
        assert response.parse().id == "resp_123"


def test_does_not_guard_responses_connect() -> None:
    client = make_sync_client(base_url="https://example.com/openai/v1", api_key="token")

    assert client.responses.connect() is not None
