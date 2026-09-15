from __future__ import annotations

import os as _os
import sys
import subprocess

import httpx2
import pytest
from httpx2 import URL

import openai
from openai import DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES


def reset_state() -> None:
    openai._reset_client()
    openai.api_key = None
    openai.admin_api_key = None
    openai.organization = None
    openai.project = None
    openai.webhook_secret = None
    openai.base_url = None
    openai.timeout = DEFAULT_TIMEOUT
    openai.max_retries = DEFAULT_MAX_RETRIES
    openai.default_headers = None
    openai.default_query = None
    openai.http_client = None
    openai.api_type = _os.environ.get("OPENAI_API_TYPE")  # type: ignore
    openai.api_version = None
    openai.azure_endpoint = None
    openai.azure_ad_token = None
    openai.azure_ad_token_provider = None
    openai._bedrock_api_key = None
    openai.bedrock_token_provider = None


@pytest.fixture(autouse=True)
def reset_state_fixture() -> None:
    reset_state()


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

    new_client = httpx2.Client()
    openai.http_client = new_client

    assert openai.completions._client._client is new_client


import contextlib
from typing import Generator

from openai.lib.azure import AzureOpenAI, MutuallyExclusiveAuthError
from openai.lib.bedrock import BedrockOpenAI


@contextlib.contextmanager
def fresh_env() -> Generator[None, None, None]:
    old = _os.environ.copy()

    try:
        _os.environ.clear()
        yield
    finally:
        _os.environ.clear()
        _os.environ.update(old)


def test_only_api_key_results_in_openai_api() -> None:
    with fresh_env():
        openai.api_type = None
        openai.api_key = "example API key"

        assert type(openai.completions._client).__name__ == "_ModuleClient"


def test_azure_api_key_env_without_api_version() -> None:
    with fresh_env():
        openai.api_type = None
        _os.environ["AZURE_OPENAI_API_KEY"] = "example API key"

        with pytest.raises(
            ValueError,
            match=r"Must provide either the `api_version` argument or the `OPENAI_API_VERSION` environment variable",
        ):
            openai.completions._client  # noqa: B018


def test_azure_api_key_and_version_env() -> None:
    with fresh_env():
        openai.api_type = None
        _os.environ["AZURE_OPENAI_API_KEY"] = "example API key"
        _os.environ["OPENAI_API_VERSION"] = "example-version"

        with pytest.raises(
            ValueError,
            match=r"Must provide one of the `base_url` or `azure_endpoint` arguments, or the `AZURE_OPENAI_ENDPOINT` environment variable",
        ):
            openai.completions._client  # noqa: B018


def test_azure_api_key_version_and_endpoint_env() -> None:
    with fresh_env():
        openai.api_type = None
        _os.environ["AZURE_OPENAI_API_KEY"] = "example API key"
        _os.environ["OPENAI_API_VERSION"] = "example-version"
        _os.environ["AZURE_OPENAI_ENDPOINT"] = "https://www.example"

        openai.completions._client  # noqa: B018

        assert openai.api_type == "azure"


def test_azure_azure_ad_token_version_and_endpoint_env() -> None:
    with fresh_env():
        openai.api_type = None
        _os.environ["AZURE_OPENAI_AD_TOKEN"] = "example AD token"
        _os.environ["OPENAI_API_VERSION"] = "example-version"
        _os.environ["AZURE_OPENAI_ENDPOINT"] = "https://www.example"

        client = openai.completions._client
        assert isinstance(client, AzureOpenAI)
        assert client._azure_ad_token == "example AD token"


def test_azure_azure_ad_token_provider_version_and_endpoint_env() -> None:
    with fresh_env():
        openai.api_type = None
        _os.environ["OPENAI_API_VERSION"] = "example-version"
        _os.environ["AZURE_OPENAI_ENDPOINT"] = "https://www.example"
        openai.azure_ad_token_provider = lambda: "token"

        client = openai.completions._client
        assert isinstance(client, AzureOpenAI)
        assert client._azure_ad_token_provider is not None
        assert client._azure_ad_token_provider() == "token"


@pytest.mark.parametrize("forced", [False, True])
@pytest.mark.parametrize("mode", ["api_key", "azure_ad_token", "azure_ad_token_provider", "environment"])
def test_azure_module_explicit_auth_precedence(forced: bool, mode: str) -> None:
    requests: list[httpx2.Request] = []

    def send(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, json={"data": []})

    with fresh_env():
        openai.api_type = "azure" if forced else None
        _os.environ["AZURE_OPENAI_API_KEY"] = "fake-ambient-key"
        _os.environ["AZURE_OPENAI_AD_TOKEN"] = "fake-ambient-token"
        _os.environ["OPENAI_API_VERSION"] = "2024-02-01"
        _os.environ["AZURE_OPENAI_ENDPOINT"] = "https://azure.test"
        if mode == "api_key":
            openai.api_key = "fake-selected"
        elif mode == "azure_ad_token":
            openai.azure_ad_token = "fake-selected"
        elif mode == "azure_ad_token_provider":
            openai.azure_ad_token_provider = lambda: "fake-selected"

        with httpx2.Client(transport=httpx2.MockTransport(send), trust_env=False) as http_client:
            openai.http_client = http_client
            openai.models.list()
            client = openai.models._client
            assert isinstance(client, AzureOpenAI)
            _, realtime_headers = client._configure_realtime("test-model", {})

        expected = (
            {"api-key": "fake-selected"}
            if mode == "api_key"
            else {"authorization": "Bearer fake-ambient-token" if mode == "environment" else "Bearer fake-selected"}
        )
        for headers in (requests[0].headers, realtime_headers):
            assert {k.lower(): v for k, v in headers.items() if k.lower() in {"authorization", "api-key"}} == expected


@pytest.mark.parametrize("forced", [False, True])
def test_azure_module_rejects_conflicting_explicit_auth(forced: bool) -> None:
    with fresh_env():
        openai.api_type = "azure" if forced else None
        openai.azure_endpoint = "https://azure.test"
        openai.api_version = "2024-02-01"
        openai.api_key = "fake-explicit-key"
        openai.azure_ad_token_provider = lambda: "fake-explicit-token"
        with pytest.raises(MutuallyExclusiveAuthError):
            _ = openai.models._client


def test_azure_module_import_does_not_make_ambient_token_explicit() -> None:
    # Exercise import-time environment handling in a fresh interpreter.
    subprocess.run(
        [
            sys.executable,
            "-c",
            "import os\n"
            "from unittest.mock import patch\n"
            "with patch.dict(os.environ, {\n"
            "    'AZURE_OPENAI_AD_TOKEN': 'fake-ambient-token',\n"
            "    'OPENAI_API_TYPE': 'azure',\n"
            "    'OPENAI_API_VERSION': '2024-02-01',\n"
            "    'AZURE_OPENAI_ENDPOINT': 'https://azure.test',\n"
            "}, clear=True):\n"
            "    import openai\n"
            "    assert openai.azure_ad_token is None\n"
            "    openai.api_key = 'fake-explicit-key'\n"
            "    client = openai.models._client\n"
            "    assert client._azure_ad_token is None\n"
            "    assert client.api_key == 'fake-explicit-key'\n"
            "    client.close()\n",
        ],
        check=True,
    )


def test_azure_module_preserves_provider_ambiguity() -> None:
    with fresh_env():
        openai.api_type = None
        _os.environ["OPENAI_API_KEY"] = "fake-openai-key"
        _os.environ["AZURE_OPENAI_AD_TOKEN"] = "fake-azure-token"
        with pytest.raises(openai.OpenAIError, match="Ambiguous use of module client"):
            _ = openai.models._client


def test_bedrock_token_and_region_env() -> None:
    with fresh_env():
        openai.api_type = "amazon-bedrock"
        _os.environ["AWS_BEARER_TOKEN_BEDROCK"] = "example Bedrock token"
        _os.environ["AWS_REGION"] = "us-west-2"

        client = openai.responses._client
        assert isinstance(client, BedrockOpenAI)
        assert client.base_url == URL("https://bedrock-mantle.us-west-2.api.aws/openai/v1/")


def test_bedrock_api_type_env() -> None:
    with fresh_env():
        _os.environ["OPENAI_API_TYPE"] = "amazon-bedrock"
        _os.environ["AWS_BEARER_TOKEN_BEDROCK"] = "example Bedrock token"
        _os.environ["AWS_REGION"] = "us-west-2"
        reset_state()

        client = openai.responses._client
        assert isinstance(client, BedrockOpenAI)
        assert openai.api_type == "amazon-bedrock"


def test_bedrock_api_type_uses_bedrock_credentials() -> None:
    with fresh_env():
        openai.api_type = "amazon-bedrock"
        _os.environ["OPENAI_API_KEY"] = "openai api key"
        _os.environ["AWS_BEARER_TOKEN_BEDROCK"] = "example Bedrock token"
        _os.environ["AWS_REGION"] = "us-west-2"

        client = openai.responses._client
        assert isinstance(client, BedrockOpenAI)
        assert client.api_key == "example Bedrock token"
        assert openai.api_key is None


def test_bedrock_api_type_uses_explicit_module_api_key() -> None:
    with fresh_env():
        openai.api_type = "amazon-bedrock"
        openai.api_key = "explicit Bedrock token"
        _os.environ["AWS_BEARER_TOKEN_BEDROCK"] = "env Bedrock token"
        _os.environ["AWS_REGION"] = "us-west-2"

        client = openai.responses._client
        assert isinstance(client, BedrockOpenAI)
        assert client.api_key == "explicit Bedrock token"
        assert openai.api_key == "explicit Bedrock token"


def test_bedrock_module_api_key_overrides_cached_env_token_after_load() -> None:
    with fresh_env():
        openai.api_type = "amazon-bedrock"
        _os.environ["AWS_BEARER_TOKEN_BEDROCK"] = "env Bedrock token"
        _os.environ["AWS_REGION"] = "us-west-2"

        client = openai.responses._client
        assert isinstance(client, BedrockOpenAI)
        assert client.api_key == "env Bedrock token"

        openai.api_key = "new Bedrock token"

        assert client.api_key == "new Bedrock token"


def test_bedrock_module_api_key_switches_cached_aws_client_to_bearer() -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={})

    with fresh_env():
        openai.api_type = "amazon-bedrock"
        openai.http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
        _os.environ["AWS_ACCESS_KEY_ID"] = "access key"
        _os.environ["AWS_SECRET_ACCESS_KEY"] = "secret key"
        _os.environ["AWS_REGION"] = "us-west-2"

        client = openai.responses._client
        assert isinstance(client, BedrockOpenAI)
        assert client._uses_aws_auth()

        openai.api_key = "new Bedrock token"
        client.get("/models", cast_to=httpx2.Response)

        assert requests[0].headers["Authorization"] == "Bearer new Bedrock token"


def test_bedrock_api_type_uses_token_provider_without_mutating_module_api_key() -> None:
    with fresh_env():
        openai.api_type = "amazon-bedrock"
        openai.bedrock_token_provider = lambda: "provider Bedrock token"
        _os.environ["AWS_REGION"] = "us-west-2"

        client = openai.responses._client
        assert isinstance(client, BedrockOpenAI)
        assert client._refresh_api_key() == "provider Bedrock token"
        assert openai.api_key is None


def test_bedrock_module_api_key_overrides_cached_token_provider() -> None:
    requests: list[httpx2.Request] = []
    provider_calls = 0

    def token_provider() -> str:
        nonlocal provider_calls
        provider_calls += 1
        raise AssertionError("the replaced token provider must not be called")

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={})

    with fresh_env():
        openai.api_type = "amazon-bedrock"
        openai.bedrock_token_provider = token_provider
        openai.http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
        _os.environ["AWS_REGION"] = "us-west-2"

        client = openai.responses._client
        assert isinstance(client, BedrockOpenAI)

        openai.api_key = "new Bedrock token"
        client.get("/models", cast_to=httpx2.Response)

    assert provider_calls == 0
    assert requests[0].headers["Authorization"] == "Bearer new Bedrock token"
