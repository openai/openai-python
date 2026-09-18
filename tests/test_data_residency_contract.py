# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import json
from typing import Any, cast, get_args

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, DataResidency

REGIONS: list[tuple[DataResidency, str]] = [
    ("global", "https://api.openai.com/v1"),
    ("us", "https://us.api.openai.com/v1"),
    ("eu", "https://eu.api.openai.com/v1"),
    ("ae", "https://ae.api.openai.com/v1"),
]


@pytest.fixture(autouse=True)
def clear_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("OPENAI_API_KEY", "OPENAI_ADMIN_KEY", "OPENAI_BASE_URL", "OPENAI_CUSTOM_HEADERS"):
        monkeypatch.delenv(name, raising=False)


def test_public_type() -> None:
    assert set(get_args(DataResidency)) == {region for region, _ in REGIONS}


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
@pytest.mark.parametrize(("region", "url"), REGIONS)
def test_constructor_and_copy_mappings(
    client_type: type[OpenAI] | type[AsyncOpenAI], region: DataResidency, url: str
) -> None:
    original = client_type(api_key="test-key", base_url="https://original.example/v1")
    regional = original.with_options(data_residency=region)
    assert regional.base_url == httpx2.URL(url.rstrip("/") + "/")
    assert client_type(api_key="test-key", data_residency=region).base_url == regional.base_url
    assert original.base_url == httpx2.URL("https://original.example/v1/")
    assert regional._client is original._client
    assert regional.copy().base_url == regional.base_url
    assert regional.with_options(data_residency=None).base_url == regional.base_url
    assert regional.with_options(base_url="https://override.example/v1").base_url == httpx2.URL(
        "https://override.example/v1/"
    )


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
@pytest.mark.parametrize("base_url", [None, "https://custom.example/v1", httpx2.URL("https://custom.example/v1")])
def test_explicit_base_url_conflicts(
    client_type: type[OpenAI] | type[AsyncOpenAI], base_url: str | httpx2.URL | None
) -> None:
    region = REGIONS[0][0]
    with pytest.raises(ValueError, match="mutually exclusive"):
        client_type(api_key="test-key", data_residency=region, base_url=base_url)
    client = client_type(api_key="test-key")
    with pytest.raises(ValueError, match="mutually exclusive"):
        client.with_options(base_url=base_url, data_residency=region)
    assert client.with_options(base_url=base_url, data_residency=None).base_url == (
        httpx2.URL(str(base_url).rstrip("/") + "/") if base_url is not None else client.base_url
    )


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
@pytest.mark.parametrize("region", ["", "UNKNOWN-RESIDENCY", 42, []])
def test_unknown_regions_fail_locally(client_type: type[OpenAI] | type[AsyncOpenAI], region: object) -> None:
    with pytest.raises(ValueError, match="Invalid `data_residency`"):
        client_type(api_key="test-key", data_residency=cast(Any, region))
    with pytest.raises(ValueError, match="Invalid `data_residency`"):
        client_type(api_key="test-key").copy(data_residency=cast(Any, region))


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
@pytest.mark.parametrize(("region", "url"), REGIONS)
def test_environment_is_not_an_explicit_conflict(
    client_type: type[OpenAI] | type[AsyncOpenAI], region: DataResidency, url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OPENAI_BASE_URL", "https://environment.example/v1")
    assert client_type(api_key="test-key", data_residency=region).base_url == httpx2.URL(url.rstrip("/") + "/")
    original = client_type(api_key="test-key", base_url=None)
    assert original.base_url == httpx2.URL("https://environment.example/v1/")
    regional = original.copy(data_residency=region)
    monkeypatch.setenv("OPENAI_BASE_URL", "https://changed.example/v1")
    assert regional.copy().base_url == regional.base_url
    assert regional.copy(base_url=None).base_url == regional.base_url


def check_request(request: httpx2.Request) -> httpx2.Response:
    assert request.url == httpx2.URL(REGIONS[0][1].rstrip("/") + "/data-residency-contract")
    assert json.loads(request.content) == {"message": "hello"}
    assert not any("residency" in name for name in request.headers)
    assert request.headers["Authorization"] == "Bearer test-key"
    return httpx2.Response(200, request=request, json={"ok": True})


def test_sync_request_only_changes_destination() -> None:
    with httpx2.Client(transport=httpx2.MockTransport(check_request), trust_env=False) as transport:
        client = OpenAI(api_key="test-key", base_url="https://original.example/v1", http_client=transport)
        result = client.with_options(data_residency=REGIONS[0][0]).post(
            "/data-residency-contract", cast_to=object, body={"message": "hello"}
        )
        assert result == {"ok": True}
        assert client.base_url == httpx2.URL("https://original.example/v1/")


async def test_async_request_only_changes_destination() -> None:
    async with httpx2.AsyncClient(transport=httpx2.MockTransport(check_request), trust_env=False) as transport:
        client = AsyncOpenAI(api_key="test-key", base_url="https://original.example/v1", http_client=transport)
        result = await client.with_options(data_residency=REGIONS[0][0]).post(
            "/data-residency-contract", cast_to=object, body={"message": "hello"}
        )
        assert result == {"ok": True}
        assert client.base_url == httpx2.URL("https://original.example/v1/")


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
@pytest.mark.parametrize(("region", "url"), REGIONS)
def test_residency_replaces_inherited_websocket_url(
    client_type: type[OpenAI] | type[AsyncOpenAI], region: DataResidency, url: str
) -> None:
    original = client_type(api_key="test-key", websocket_base_url="wss://original.example/v1")
    regional = original.with_options(data_residency=region)
    assert original.copy().websocket_base_url == original.websocket_base_url
    assert original.copy(data_residency=None).websocket_base_url == original.websocket_base_url
    assert regional.websocket_base_url is None
    assert regional.copy().websocket_base_url is None
    assert regional.base_url == httpx2.URL(url.rstrip("/") + "/")
    for websocket_base_url in ("wss://custom.example/v1", httpx2.URL("wss://custom.example/v1")):
        with pytest.raises(ValueError, match="`data_residency` and `websocket_base_url`"):
            client_type(api_key="test-key", data_residency=region, websocket_base_url=websocket_base_url)
        with pytest.raises(ValueError, match="`data_residency` and `websocket_base_url`"):
            original.with_options(data_residency=region, websocket_base_url=websocket_base_url)
    assert original.with_options(data_residency=region, websocket_base_url=None).websocket_base_url is None
