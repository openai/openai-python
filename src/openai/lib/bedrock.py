from __future__ import annotations

import os
import re
import inspect
from typing import Any, Mapping, Callable, Awaitable, cast
from typing_extensions import Self, override

import httpx

from ..auth import WorkloadIdentity
from .._types import NOT_GIVEN, Timeout, NotGiven
from .._utils import is_given
from .._client import OpenAI, AsyncOpenAI
from .._models import SecurityOptions, FinalRequestOptions
from .._exceptions import OpenAIError
from .._base_client import DEFAULT_MAX_RETRIES

BedrockTokenProvider = Callable[[], str]
AsyncBedrockTokenProvider = Callable[[], "str | Awaitable[str]"]


def _normalize_bedrock_base_url(base_url: str | httpx.URL) -> httpx.URL:
    """Normalize a Bedrock Responses URL variant back to the provider API root."""
    url = httpx.URL(base_url)
    path = url.path.rstrip("/")
    responses_match = re.search(r"/responses(?:/.*)?$", path)
    if responses_match is not None:
        path = path[: responses_match.start()]

    return url.copy_with(path=path or "/")


def _resolve_bedrock_base_url(base_url: str | httpx.URL | None, aws_region: str | None) -> httpx.URL:
    """Resolve Bedrock base URL precedence from explicit, env, then region config."""
    if isinstance(base_url, str) and not base_url.strip():
        base_url = None

    if base_url is None:
        env_base_url = os.environ.get("AWS_BEDROCK_BASE_URL")
        if env_base_url is not None and env_base_url.strip():
            base_url = env_base_url

    if base_url is None:
        region = aws_region or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
        if region is None or not region.strip():
            raise OpenAIError(
                "Must provide one of the `base_url` or `aws_region` arguments, or set the "
                "`AWS_BEDROCK_BASE_URL`, `AWS_REGION`, or `AWS_DEFAULT_REGION` environment variable."
            )

        base_url = f"https://bedrock-mantle.{region}.api.aws/openai/v1"

    return _normalize_bedrock_base_url(base_url)


def _uses_region_derived_bedrock_base_url(base_url: str | httpx.URL | None) -> bool:
    if isinstance(base_url, str) and not base_url.strip():
        base_url = None

    if base_url is not None:
        return False

    env_base_url = os.environ.get("AWS_BEDROCK_BASE_URL")
    return env_base_url is None or not env_base_url.strip()


def _bedrock_token_provider(provider: BedrockTokenProvider) -> BedrockTokenProvider:
    """Adapt a sync Bedrock token provider to the base client's api_key callback."""

    def get_token() -> str:
        token = cast(object, provider())
        if not isinstance(token, str) or not token:
            raise ValueError(f"Expected `bedrock_token_provider` argument to return a string but it returned {token}")

        return token

    return get_token


def _async_bedrock_token_provider(provider: AsyncBedrockTokenProvider) -> Callable[[], Awaitable[str]]:
    """Adapt a sync or async Bedrock token provider to the async api_key callback."""

    async def get_token() -> str:
        token = cast(object, provider())
        if inspect.isawaitable(token):
            token = await token

        if not isinstance(token, str) or not token:
            raise ValueError(f"Expected `bedrock_token_provider` argument to return a string but it returned {token}")

        return token

    return get_token


class BedrockOpenAI(OpenAI):
    """API client for Amazon Bedrock's OpenAI-compatible endpoint."""

    _bedrock_token_provider: BedrockTokenProvider | None
    _uses_region_derived_base_url: bool
    aws_region: str | None

    def __init__(
        self,
        *,
        api_key: str | None = None,
        bedrock_token_provider: BedrockTokenProvider | None = None,
        aws_region: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        webhook_secret: str | None = None,
        base_url: str | httpx.URL | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.Client | None = None,
        _strict_response_validation: bool = False,
        _enforce_credentials: bool = True,
    ) -> None:
        """Construct a new synchronous Amazon Bedrock client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `AWS_BEARER_TOKEN_BEDROCK`
        - `aws_region` from `AWS_REGION` or `AWS_DEFAULT_REGION` when `base_url` and `AWS_BEDROCK_BASE_URL` are not set
        - `base_url` from `AWS_BEDROCK_BASE_URL`

        `bedrock_token_provider` is invoked before each request when provided.
        """
        if api_key is None and bedrock_token_provider is None:
            api_key = os.environ.get("AWS_BEARER_TOKEN_BEDROCK")

        if callable(cast(object, api_key)):
            raise OpenAIError("Pass refreshable Bedrock credentials via `bedrock_token_provider`, not `api_key`.")

        if api_key is not None and bedrock_token_provider is not None:
            raise OpenAIError("The `api_key` and `bedrock_token_provider` arguments are mutually exclusive.")

        if _enforce_credentials and not api_key and bedrock_token_provider is None:
            raise OpenAIError(
                "Missing credentials. Please pass an `api_key` or `bedrock_token_provider`, or set the "
                "`AWS_BEARER_TOKEN_BEDROCK` environment variable."
            )

        self._bedrock_token_provider = bedrock_token_provider
        self._uses_region_derived_base_url = _uses_region_derived_bedrock_base_url(base_url)
        self.aws_region = aws_region

        super().__init__(
            api_key=_bedrock_token_provider(bedrock_token_provider)
            if bedrock_token_provider is not None
            else api_key or "",
            admin_api_key="",
            organization=organization,
            project=project,
            webhook_secret=webhook_secret,
            base_url=_resolve_bedrock_base_url(base_url, aws_region),
            websocket_base_url=websocket_base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
            _enforce_credentials=False,
        )

    @override
    def _auth_headers(self, security: SecurityOptions) -> dict[str, str]:
        if security.get("bearer_auth", False) or security.get("admin_api_key_auth", False):
            return self._bearer_auth

        return {}

    @override
    def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
        if (
            self._api_key_provider is not None
            and options.security.get("admin_api_key_auth", False)
            and not options.security.get("bearer_auth", False)
        ):
            self._refresh_api_key()

        return super()._prepare_options(options)

    @override
    def copy(
        self,
        *,
        api_key: str | BedrockTokenProvider | None = None,
        admin_api_key: str | None = None,
        workload_identity: WorkloadIdentity | None = None,
        bedrock_token_provider: BedrockTokenProvider | None = None,
        aws_region: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        webhook_secret: str | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _enforce_credentials: bool | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        if callable(api_key):
            raise OpenAIError("Pass refreshable Bedrock credentials via `bedrock_token_provider`, not `api_key`.")

        if admin_api_key is not None or workload_identity is not None:
            raise OpenAIError("BedrockOpenAI only supports Bedrock bearer token authentication.")

        if api_key is not None and bedrock_token_provider is not None:
            raise OpenAIError("The `api_key` and `bedrock_token_provider` arguments are mutually exclusive.")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        if api_key is not None:
            next_token_provider = None
        elif bedrock_token_provider is not None:
            next_token_provider = bedrock_token_provider
        else:
            next_token_provider = self._bedrock_token_provider

        next_api_key = api_key if api_key is not None else (None if next_token_provider is not None else self.api_key)
        next_base_url = base_url
        if next_base_url is None and not (aws_region is not None and self._uses_region_derived_base_url):
            next_base_url = self.base_url

        return self.__class__(
            api_key=next_api_key,
            bedrock_token_provider=next_token_provider,
            aws_region=aws_region if aws_region is not None else self.aws_region,
            organization=organization if organization is not None else self.organization,
            project=project if project is not None else self.project,
            webhook_secret=webhook_secret if webhook_secret is not None else self.webhook_secret,
            websocket_base_url=websocket_base_url if websocket_base_url is not None else self.websocket_base_url,
            base_url=next_base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client or self._client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            _enforce_credentials=True if _enforce_credentials is None else _enforce_credentials,
            **_extra_kwargs,
        )

    with_options = copy


class AsyncBedrockOpenAI(AsyncOpenAI):
    """Async API client for Amazon Bedrock's OpenAI-compatible endpoint."""

    _bedrock_token_provider: AsyncBedrockTokenProvider | None
    _uses_region_derived_base_url: bool
    aws_region: str | None

    def __init__(
        self,
        *,
        api_key: str | None = None,
        bedrock_token_provider: AsyncBedrockTokenProvider | None = None,
        aws_region: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        webhook_secret: str | None = None,
        base_url: str | httpx.URL | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.AsyncClient | None = None,
        _strict_response_validation: bool = False,
        _enforce_credentials: bool = True,
    ) -> None:
        """Construct a new asynchronous Amazon Bedrock client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `AWS_BEARER_TOKEN_BEDROCK`
        - `aws_region` from `AWS_REGION` or `AWS_DEFAULT_REGION` when `base_url` and `AWS_BEDROCK_BASE_URL` are not set
        - `base_url` from `AWS_BEDROCK_BASE_URL`

        `bedrock_token_provider` is invoked before each request when provided.
        """
        if api_key is None and bedrock_token_provider is None:
            api_key = os.environ.get("AWS_BEARER_TOKEN_BEDROCK")

        if callable(cast(object, api_key)):
            raise OpenAIError("Pass refreshable Bedrock credentials via `bedrock_token_provider`, not `api_key`.")

        if api_key is not None and bedrock_token_provider is not None:
            raise OpenAIError("The `api_key` and `bedrock_token_provider` arguments are mutually exclusive.")

        if _enforce_credentials and not api_key and bedrock_token_provider is None:
            raise OpenAIError(
                "Missing credentials. Please pass an `api_key` or `bedrock_token_provider`, or set the "
                "`AWS_BEARER_TOKEN_BEDROCK` environment variable."
            )

        self._bedrock_token_provider = bedrock_token_provider
        self._uses_region_derived_base_url = _uses_region_derived_bedrock_base_url(base_url)
        self.aws_region = aws_region

        super().__init__(
            api_key=(
                _async_bedrock_token_provider(bedrock_token_provider)
                if bedrock_token_provider is not None
                else api_key or ""
            ),
            admin_api_key="",
            organization=organization,
            project=project,
            webhook_secret=webhook_secret,
            base_url=_resolve_bedrock_base_url(base_url, aws_region),
            websocket_base_url=websocket_base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
            _enforce_credentials=False,
        )

    @override
    def _auth_headers(self, security: SecurityOptions) -> dict[str, str]:
        if security.get("bearer_auth", False) or security.get("admin_api_key_auth", False):
            return self._bearer_auth

        return {}

    @override
    async def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
        if (
            self._api_key_provider is not None
            and options.security.get("admin_api_key_auth", False)
            and not options.security.get("bearer_auth", False)
        ):
            await self._refresh_api_key()

        return await super()._prepare_options(options)

    @override
    def copy(
        self,
        *,
        api_key: str | AsyncBedrockTokenProvider | None = None,
        admin_api_key: str | None = None,
        workload_identity: WorkloadIdentity | None = None,
        bedrock_token_provider: AsyncBedrockTokenProvider | None = None,
        aws_region: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        webhook_secret: str | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _enforce_credentials: bool | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        if callable(api_key):
            raise OpenAIError("Pass refreshable Bedrock credentials via `bedrock_token_provider`, not `api_key`.")

        if admin_api_key is not None or workload_identity is not None:
            raise OpenAIError("AsyncBedrockOpenAI only supports Bedrock bearer token authentication.")

        if api_key is not None and bedrock_token_provider is not None:
            raise OpenAIError("The `api_key` and `bedrock_token_provider` arguments are mutually exclusive.")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        if api_key is not None:
            next_token_provider = None
        elif bedrock_token_provider is not None:
            next_token_provider = bedrock_token_provider
        else:
            next_token_provider = self._bedrock_token_provider

        next_api_key = api_key if api_key is not None else (None if next_token_provider is not None else self.api_key)
        next_base_url = base_url
        if next_base_url is None and not (aws_region is not None and self._uses_region_derived_base_url):
            next_base_url = self.base_url

        return self.__class__(
            api_key=next_api_key,
            bedrock_token_provider=next_token_provider,
            aws_region=aws_region if aws_region is not None else self.aws_region,
            organization=organization if organization is not None else self.organization,
            project=project if project is not None else self.project,
            webhook_secret=webhook_secret if webhook_secret is not None else self.webhook_secret,
            websocket_base_url=websocket_base_url if websocket_base_url is not None else self.websocket_base_url,
            base_url=next_base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client or self._client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            _enforce_credentials=True if _enforce_credentials is None else _enforce_credentials,
            **_extra_kwargs,
        )

    with_options = copy
