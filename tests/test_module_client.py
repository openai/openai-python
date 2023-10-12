# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os as _os

import httpx
import pytest
from httpx import URL

import openai
from openai import DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES


@pytest.fixture(autouse=True)
def reset_state() -> None:
    openai._reset_client()
    openai.api_key = _os.environ.get("OPENAI_API_KEY") or "My API Key"
    openai.organization = _os.environ.get("OPENAI_ORG_ID")
    openai.base_url = None
    openai.timeout = DEFAULT_TIMEOUT
    openai.max_retries = DEFAULT_MAX_RETRIES
    openai.default_headers = None
    openai.default_query = None
    openai.http_client = None


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


def test_http_client_option() -> None:
    assert openai.http_client is None

    original_http_client = openai.completions._client._client
    assert original_http_client is not None

    new_client = httpx.Client()
    openai.http_client = new_client

    assert openai.completions._client._client is new_client
