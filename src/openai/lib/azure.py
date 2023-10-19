from __future__ import annotations

import os
import inspect
from typing import Callable, Mapping, Awaitable, overload
from typing_extensions import Literal

import httpx

from .._types import NOT_GIVEN, Timeout, NotGiven, Omit
from .._utils import is_mapping, is_given
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


AzureApiType = Literal["azure", "azure_ad"]
GetAzureADToken = Callable[[], str]
AsyncGetAzureADToken = Callable[[], "str | Awaitable[str]"]


# we need to use a sentinel API key value for Azure AD
# as we don't want to make the `api_key` in the main client Optional
# and Azure AD tokens may be retrieved on a per-request basis
API_KEY_SENTINEL = "".join(["<", "missing API key", ">"])


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
    _api_type: AzureApiType

    @overload
    def __init__(
        self,
        *,
        api_version: str,
        endpoint: str,
        deployment: str | None = None,
        api_type: AzureApiType | None = None,
        api_key: str | None = None,
        get_ad_token: GetAzureADToken | None = None,
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
        api_type: AzureApiType | None = None,
        api_key: str | None = None,
        get_ad_token: GetAzureADToken | None = None,
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
        api_type: AzureApiType | None = None,
        get_ad_token: GetAzureADToken | None = None,
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
        if api_key is None and get_ad_token is None:
            raise OpenAIError(
                "The api_key client option must be set either by passing api_key to the client or by setting the AZURE_OPENAI_API_KEY environment variable; If you're using Azure AD you should pass a `get_ad_token` argument."
            )

        if api_type is None:
            if get_ad_token:
                api_type = "azure_ad"
            else:
                api_type = "azure"

        self._api_type = api_type

        if default_query is None:
            default_query = {"api-version": api_version}
        else:
            default_query = {"api-version": api_version, **default_query}

        if base_url is None:
            if endpoint is None:
                raise ValueError("If base_url is not given, then endpoint must be given")

            if deployment is not None:
                base_url = f"{endpoint}/openai/deployments/{deployment}"
            else:
                base_url = f"{endpoint}/openai"

        if api_key is None:
            api_key = API_KEY_SENTINEL

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
        self._get_ad_token = get_ad_token

    def _prepare_options(self, options: FinalRequestOptions) -> None:
        headers: dict[str, str | Omit] = {**options.headers} if is_given(options.headers) else {}
        options.headers = headers

        if self._get_ad_token is not None:
            auth = self._get_ad_token()
            if not auth or not isinstance(auth, str):  # pyright: ignore[reportUnnecessaryIsInstance]
                raise ValueError(
                    f"Expected `get_ad_token` argument to return a string but it returned {auth}",
                )
        else:
            auth = self.api_key

        if self._api_type == 'azure':
            if headers.get("api-key") is None:
                headers["api-key"] = auth
        else:
            if headers.get('Authorization') is None:
                headers['Authorization'] = f'Bearer {auth}'

        return super()._prepare_options(options)


class AsyncAzureOpenAI(BaseAzureClient, AsyncOpenAI):
    _api_type: AzureApiType

    @overload
    def __init__(
        self,
        *,
        api_version: str,
        endpoint: str,
        deployment: str | None = None,
        api_key: str | None = None,
        api_type: AzureApiType | None = None,
        get_ad_token: AsyncGetAzureADToken | None = None,
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
        api_type: AzureApiType | None = None,
        get_ad_token: AsyncGetAzureADToken | None = None,
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
        api_type: AzureApiType | None = None,
        get_ad_token: AsyncGetAzureADToken | None = None,
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
        if api_key is None and get_ad_token is None:
            raise OpenAIError(
                "The api_key client option must be set either by passing api_key to the client or by setting the AZURE_OPENAI_API_KEY environment variable; If you're using Azure AD you should pass a `get_ad_token` argument."
            )

        if api_type is None:
            if get_ad_token:
                api_type = "azure_ad"
            else:
                api_type = "azure"

        self._api_type = api_type

        if default_query is None:
            default_query = {"api-version": api_version}
        else:
            default_query = {"api-version": api_version, **default_query}

        if base_url is None:
            if endpoint is None:
                raise ValueError("If base_url is not given, then endpoint must be given")

            if deployment is not None:
                base_url = f"{endpoint}/openai/deployments/{deployment}"
            else:
                base_url = f"{endpoint}/openai"

        if api_key is None:
            api_key = API_KEY_SENTINEL

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
        self._get_ad_token = get_ad_token

    async def _prepare_options(self, options: FinalRequestOptions) -> None:
        headers: dict[str, str | Omit] = {**options.headers} if is_given(options.headers) else {}
        options.headers = headers

        if self._get_ad_token is not None:
            result = self._get_ad_token()
            if inspect.isawaitable(result):
                auth = await result
            else:
                auth = result

            if not auth or not isinstance(auth, str):  # pyright: ignore[reportUnnecessaryIsInstance]
                raise ValueError(
                    f"Expected `get_ad_token` argument to return a string but it returned {auth}",
                )
        else:
            auth = self.api_key

        if self._api_type == 'azure':
            if headers.get("api-key") is None:
                headers["api-key"] = auth
        else:
            if headers.get('Authorization') is None:
                headers['Authorization'] = f'Bearer {auth}'

        return await super()._prepare_options(options)
