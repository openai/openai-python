# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os as _os

import httpx
import pytest
from httpx import URL

import openai
from openai import DEFAULT_LIMITS, DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES


@pytest.fixture(autouse=True)
def reset_state() -> None:
    openai._reset_client()
    openai.api_key = _os.environ.get("OPENAI_API_KEY") or "my API Key"
    openai.organization = _os.environ.get("OPENAI_ORG_ID") or None
    openai.base_url = None
    openai.timeout = DEFAULT_TIMEOUT
    openai.max_retries = DEFAULT_MAX_RETRIES
    openai.default_headers = None
    openai.default_query = None
    openai.transport = None
    openai.proxies = None
    openai.connection_pool_limits = DEFAULT_LIMITS


def test_api_key_option() -> None:
    openai.api_key = "foo"

    assert openai.api_key is "foo"
    assert openai.completions._client.api_key is "foo"

    first_client = openai.completions._client

    openai.api_key = "bar"

    assert first_client is openai.completions._client  # should remain cached


def test_base_url_option() -> None:
    assert openai.base_url is None
    assert openai.completions._client.base_url == URL("https://api.openai.com/v1/")

    openai.base_url = "http://foo.com"

    assert openai.base_url == URL("http://foo.com")
    assert openai.completions._client.base_url == URL("http://foo.com")


def test_timeout_option() -> None:
    assert openai.timeout == openai.DEFAULT_TIMEOUT
    assert openai.completions._client.timeout == openai.DEFAULT_TIMEOUT

    openai.timeout = 3

    assert openai.timeout == 3
    assert openai.completions._client.timeout == 3


def test_max_retries_option() -> None:
    assert openai.max_retries == openai.DEFAULT_MAX_RETRIES
    assert openai.completions._client.max_retries == openai.DEFAULT_MAX_RETRIES

    openai.max_retries = 1

    assert openai.max_retries == 1
    assert openai.completions._client.max_retries == 1


def test_default_headers_option() -> None:
    assert openai.default_headers == None

    openai.default_headers = {"Foo": "Bar"}

    assert openai.default_headers["Foo"] == "Bar"
    assert openai.completions._client.default_headers["Foo"] == "Bar"


def test_default_query_option() -> None:
    assert openai.default_query is None
    assert openai.completions._client._custom_query == {}

    openai.default_query = {"Foo": {"nested": 1}}

    assert openai.default_query["Foo"] == {"nested": 1}
    assert openai.completions._client._custom_query["Foo"] == {"nested": 1}


def test_transport_option() -> None:
    assert openai.transport is None

    first_client = openai.completions._client

    transport = httpx.MockTransport(lambda: None)
    openai.transport = transport

    second_client = openai.completions._client
    assert first_client is not second_client
    assert second_client is openai.completions._client  # should be cached

    assert first_client._transport is None
    assert second_client._transport is transport


def test_proxies_option() -> None:
    assert openai.proxies is None

    first_client = openai.completions._client

    openai.proxies = {"http://": "http://example.com"}

    second_client = openai.completions._client
    assert first_client is not second_client
    assert second_client is openai.completions._client  # cached

    assert first_client._proxies is None
    assert second_client._proxies == {"http://": "http://example.com"}


def test_connection_pool_limits_option() -> None:
    assert openai.connection_pool_limits is DEFAULT_LIMITS

    first_client = openai.completions._client

    limits = httpx.Limits(max_connections=1000)
    openai.connection_pool_limits = limits

    second_client = openai.completions._client
    assert first_client is not second_client
    assert second_client is openai.completions._client  # cached

    assert first_client._limits is DEFAULT_LIMITS
    assert second_client._limits is limits
