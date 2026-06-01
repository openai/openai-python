from __future__ import annotations

import json
from typing import Any, Union, Protocol, cast

import httpx
import pytest
from httpx import URL
from respx import MockRouter

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
        with pytest.raises(OpenAIError, match="Must provide one of the `base_url` or `aws_region`"):
            client_cls(api_key="token")


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_does_not_use_openai_api_key(client_cls: type[Client]) -> None:
    with update_env(
        OPENAI_API_KEY="openai token",
        AWS_BEARER_TOKEN_BEDROCK=Omit(),
        AWS_BEDROCK_BASE_URL="https://example.com/openai/v1",
    ):
        with pytest.raises(OpenAIError, match="AWS_BEARER_TOKEN_BEDROCK"):
            client_cls()


@pytest.mark.parametrize("client_cls", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_rejects_static_token_and_provider(client_cls: type[Client]) -> None:
    with pytest.raises(OpenAIError, match="mutually exclusive"):
        client_cls(
            base_url="https://example.com/openai/v1",
            api_key="token",
            bedrock_token_provider=lambda: "provider token",
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


def test_preserves_token_provider_across_with_options() -> None:
    client = BedrockOpenAI(
        base_url="https://example.com/openai/v1",
        bedrock_token_provider=lambda: "provider token",
        http_client=httpx.Client(trust_env=False),
    )

    copied_client = client.with_options(timeout=1)

    assert copied_client._refresh_api_key() == "provider token"


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

    with pytest.raises(OpenAIError, match="only supports Bedrock bearer token authentication"):
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
