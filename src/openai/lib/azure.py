from __future__ import annotations

import os
from typing import Mapping, overload

import httpx

from .._types import NOT_GIVEN, Timeout, NotGiven
from .._utils import is_mapping
from .._client import OpenAI, AsyncOpenAI
from .._models import FinalRequestOptions
from .._exceptions import OpenAIError
from .._base_client import DEFAULT_MAX_RETRIES, BaseClient


_deployments_endpoints = set(
    [
        "/completions",
        "/chat/completions",
        "/embeddings",
        "/audio/transcriptions",
        "/audio/translations",
    ]
)


class BaseAzureClient(BaseClient):
    def _build_request(
        self,
        options: FinalRequestOptions,
    ) -> httpx.Request:
        if options.url in _deployments_endpoints and is_mapping(options.json_data):
            model = options.json_data.get("model")
            if model is not None and not "/deployments" in str(self.base_url):
                options.url = f"/deployments/{model}{options.url}"

        return super()._build_request(options)


class AzureOpenAI(BaseAzureClient, OpenAI):
    @overload
    def __init__(
        self,
        *,
        api_version: str,
        endpoint: str,
        deployment: str | None = None,
        api_key: str | None = None,
        organization: str | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.Client | None = None,
        _strict_response_validation: bool = False,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        *,
        api_version: str,
        base_url: str,
        api_key: str | None = None,
        organization: str | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.Client | None = None,
        _strict_response_validation: bool = False,
    ) -> None:
        ...

    def __init__(
        self,
        *,
        api_version: str,
        endpoint: str | None = None,
        deployment: str | None = None,
        api_key: str | None = None,
        organization: str | None = None,
        base_url: str | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.Client | None = None,
        _strict_response_validation: bool = False,
    ) -> None:
        if api_key is None:
            api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        if api_key is None:
            raise OpenAIError(
                "The api_key client option must be set either by passing api_key to the client or by setting the AZURE_OPENAI_API_KEY environment variable"
            )

        if default_headers is None:
            default_headers = {"api-key": api_key}
        else:
            default_headers = {"api-key": api_key, **default_headers}

        if default_query is None:
            default_query = {"api-version": api_version}
        else:
            default_query = {"api-version": api_version, **default_query}

        if base_url is None:
            if endpoint is None:
                raise ValueError("If base_url is not given, then endpoint must be given")

            if deployment is not None:
                base_url = f"https://{endpoint}.openai.azure.com/openai/deployments/{deployment}"
            else:
                base_url = f"https://{endpoint}.openai.azure.com/openai"

        super().__init__(
            api_key=api_key,
            organization=organization,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
        )


class AsyncAzureOpenAI(BaseAzureClient, AsyncOpenAI):
    @overload
    def __init__(
        self,
        *,
        api_version: str,
        endpoint: str,
        deployment: str | None = None,
        api_key: str | None = None,
        organization: str | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.AsyncClient | None = None,
        _strict_response_validation: bool = False,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        *,
        api_version: str,
        base_url: str,
        api_key: str | None = None,
        organization: str | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.AsyncClient | None = None,
        _strict_response_validation: bool = False,
    ) -> None:
        ...

    def __init__(
        self,
        *,
        api_version: str,
        endpoint: str | None = None,
        deployment: str | None = None,
        api_key: str | None = None,
        organization: str | None = None,
        base_url: str | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.AsyncClient | None = None,
        _strict_response_validation: bool = False,
    ) -> None:
        if api_key is None:
            api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        if api_key is None:
            raise OpenAIError(
                "The api_key client option must be set either by passing api_key to the client or by setting the AZURE_OPENAI_API_KEY environment variable"
            )

        if default_headers is None:
            default_headers = {"api-key": api_key}
        else:
            default_headers = {"api-key": api_key, **default_headers}

        if default_query is None:
            default_query = {"api-version": api_version}
        else:
            default_query = {"api-version": api_version, **default_query}

        if base_url is None:
            if endpoint is None:
                raise ValueError("If base_url is not given, then endpoint must be given")

            if deployment is not None:
                base_url = f"https://{endpoint}.openai.azure.com/openai/deployments/{deployment}"
            else:
                base_url = f"https://{endpoint}.openai.azure.com/openai"

        super().__init__(
            api_key=api_key,
            organization=organization,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
        )
