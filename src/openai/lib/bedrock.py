from __future__ import annotations

import os
import re
import inspect
from typing import Any, Literal, Mapping, Callable, Awaitable, cast
from dataclasses import replace
from typing_extensions import Self, Unpack, override

import httpx

from ..auth import WorkloadIdentity
from .._types import NOT_GIVEN, Omit, Headers, Timeout, NotGiven, HttpxSendArgs
from .._utils import asyncify, is_given
from .._client import OpenAI, AsyncOpenAI
from .._models import SecurityOptions, FinalRequestOptions
from .._exceptions import OpenAIError
from .._base_client import DEFAULT_MAX_RETRIES
from ._bedrock_auth import (
    BedrockAwsAuth as _BedrockAwsAuth,
    BedrockAwsAuthConfig as _BedrockAwsAuthConfig,
    AwsCredentialsProvider,
    BedrockBearerAuthConfig as _BedrockBearerAuthConfig,
    resolve_aws_region as _resolve_aws_region,
    has_explicit_aws_auth as _has_explicit_aws_auth,
    resolve_bedrock_env_token as _resolve_bedrock_env_token,
    validate_explicit_aws_auth as _validate_explicit_aws_auth,
    resolve_aws_region_with_source as _resolve_aws_region_with_source,
)

BedrockTokenProvider = Callable[[], str]
AsyncBedrockTokenProvider = Callable[[], "str | Awaitable[str]"]

_BEDROCK_AUTH_INTENT_EXTENSION = "openai.bedrock_auth_intent"
_BEDROCK_AUTH_INTENT_DEFAULT = "default"
_BEDROCK_AUTH_INTENT_OMIT = "omit"
_BEDROCK_AUTH_INTENT_OVERRIDE = "override"
_BEDROCK_MAX_RETRIES_EXTENSION = "openai.bedrock_max_retries"
_AWS_SIGNING_HEADERS = ("authorization", "x-amz-content-sha256", "x-amz-date", "x-amz-security-token")


def _authorization_intent(*header_sets: Mapping[str, str | Omit]) -> str:
    intent = _BEDROCK_AUTH_INTENT_DEFAULT
    for headers in header_sets:
        for name, value in headers.items():
            if name.lower() == "authorization":
                intent = _BEDROCK_AUTH_INTENT_OMIT if isinstance(value, Omit) else _BEDROCK_AUTH_INTENT_OVERRIDE
    return intent


def _same_origin(left: httpx.URL, right: httpx.URL) -> bool:
    return (left.scheme, left.host, left.port) == (right.scheme, right.host, right.port)


def _constructor_accepts_keyword(constructor: Callable[..., object], name: str) -> bool:
    try:
        parameters = inspect.signature(constructor).parameters
    except (TypeError, ValueError):
        return False

    return name in parameters or any(
        parameter.kind is inspect.Parameter.VAR_KEYWORD for parameter in parameters.values()
    )


def _body_for_signing(request: httpx.Request) -> bytes | None:
    try:
        return request.content
    except httpx.RequestNotRead as exc:
        max_retries = request.extensions.get(_BEDROCK_MAX_RETRIES_EXTENSION)
        if max_retries == 0:
            return None

        raise OpenAIError(
            "Bedrock SigV4 authentication requires a replayable request body when retries are enabled. "
            "Buffer the body, set `max_retries=0` to use `UNSIGNED-PAYLOAD`, or use bearer authentication."
        ) from exc


def _normalize_bedrock_base_url(base_url: str | httpx.URL) -> httpx.URL:
    """Normalize a Bedrock Responses URL variant back to the provider API root."""
    url = httpx.URL(base_url)
    path = url.path.rstrip("/")
    responses_match = re.search(r"/responses(?:/.*)?$", path)
    if responses_match is not None:
        path = path[: responses_match.start()]

    return url.copy_with(path=path or "/")


def _configured_aws_region(aws_region: str | None) -> str | None:
    region = aws_region if aws_region is not None and aws_region.strip() else None
    region = region or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    return region.strip() if region is not None and region.strip() else None


def _configured_aws_region_source(aws_region: str | None) -> Literal["explicit", "environment"] | None:
    if aws_region is not None and aws_region.strip():
        return "explicit"
    environment_region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    if environment_region is not None and environment_region.strip():
        return "environment"
    return None


def _resolve_bedrock_base_url(
    base_url: str | httpx.URL | None,
    aws_region: str | None,
    *,
    use_environment: bool = True,
) -> httpx.URL:
    """Resolve Bedrock base URL precedence from explicit, env, then region config."""
    if isinstance(base_url, str) and not base_url.strip():
        base_url = None

    if base_url is None and use_environment:
        env_base_url = os.environ.get("AWS_BEDROCK_BASE_URL")
        if env_base_url is not None and env_base_url.strip():
            base_url = env_base_url

    if base_url is None:
        region = _configured_aws_region(aws_region)
        if region is None:
            raise OpenAIError(
                "Bedrock requires an AWS region. Pass `aws_region`, or set `AWS_REGION` or `AWS_DEFAULT_REGION`."
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


def _resolve_bedrock_auth(
    *,
    api_key: str | None,
    token_provider: object | None,
    aws_region: str | None,
    aws_profile: str | None,
    aws_access_key_id: str | None,
    aws_secret_access_key: str | None,
    aws_session_token: str | None,
    aws_credentials_provider: AwsCredentialsProvider | None,
    auth_config: _BedrockBearerAuthConfig | _BedrockAwsAuthConfig | None,
    enforce_credentials: bool,
) -> tuple[_BedrockBearerAuthConfig | _BedrockAwsAuthConfig, _BedrockAwsAuth | None, str | None, str | None]:
    if auth_config is not None:
        if isinstance(auth_config, _BedrockAwsAuthConfig):
            aws_auth = _BedrockAwsAuth(auth_config) if enforce_credentials else None
            return auth_config, aws_auth, api_key, auth_config.region

        return auth_config, None, api_key, aws_region

    explicit_bearer_auth = api_key is not None or token_provider is not None
    explicit_aws_auth = _has_explicit_aws_auth(
        aws_profile=aws_profile,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        aws_credentials_provider=aws_credentials_provider,
    )
    if explicit_bearer_auth and explicit_aws_auth:
        raise OpenAIError(
            "Bedrock authentication is ambiguous. Configure exactly one explicit mode: bearer credential, "
            "static AWS credentials, profile, or credential provider."
        )

    _validate_explicit_aws_auth(
        aws_profile=aws_profile,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        aws_credentials_provider=aws_credentials_provider,
    )

    if explicit_bearer_auth:
        source: Literal["explicit", "provider"] = "provider" if token_provider is not None else "explicit"
        return (
            _BedrockBearerAuthConfig(source=source, region_source=_configured_aws_region_source(aws_region)),
            None,
            api_key,
            _configured_aws_region(aws_region),
        )

    if not explicit_aws_auth:
        api_key = _resolve_bedrock_env_token()
        if api_key is not None:
            return (
                _BedrockBearerAuthConfig(
                    source="environment",
                    region_source=_configured_aws_region_source(aws_region),
                ),
                None,
                api_key,
                _configured_aws_region(aws_region),
            )

    if enforce_credentials:
        aws_auth = _BedrockAwsAuth.resolve(
            region=aws_region,
            profile=aws_profile,
            access_key_id=aws_access_key_id,
            secret_access_key=aws_secret_access_key,
            session_token=aws_session_token,
            credentials_provider=aws_credentials_provider,
        )
        return aws_auth.config, aws_auth, None, aws_auth.config.region

    resolved_region, region_source = _resolve_aws_region_with_source(aws_region)
    aws_source: Literal["static", "profile", "provider", "default"]
    if aws_access_key_id is not None:
        aws_source = "static"
    elif aws_profile is not None:
        aws_source = "profile"
    elif aws_credentials_provider is not None:
        aws_source = "provider"
    else:
        aws_source = "default"
    return (
        _BedrockAwsAuthConfig(
            region=resolved_region,
            source=aws_source,
            region_source=region_source,
            profile=aws_profile,
            access_key_id=aws_access_key_id,
            secret_access_key=aws_secret_access_key,
            session_token=aws_session_token,
            credentials_provider=aws_credentials_provider,
        ),
        None,
        None,
        resolved_region,
    )


class BedrockOpenAI(OpenAI):
    """API client for Amazon Bedrock's OpenAI-compatible endpoint."""

    _bedrock_token_provider: BedrockTokenProvider | None
    _bedrock_auth_config: _BedrockBearerAuthConfig | _BedrockAwsAuthConfig
    _bedrock_aws_auth: _BedrockAwsAuth | None
    _uses_region_derived_base_url: bool
    aws_region: str | None

    def __init__(
        self,
        *,
        api_key: str | None = None,
        bedrock_token_provider: BedrockTokenProvider | None = None,
        aws_region: str | None = None,
        aws_profile: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        aws_session_token: str | None = None,
        aws_credentials_provider: AwsCredentialsProvider | None = None,
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
        _auth_config: _BedrockBearerAuthConfig | _BedrockAwsAuthConfig | None = None,
        _base_url_is_region_derived: bool | None = None,
    ) -> None:
        """Construct a new synchronous Amazon Bedrock client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - bearer authentication from `AWS_BEARER_TOKEN_BEDROCK`
        - `aws_region` from `AWS_REGION` or `AWS_DEFAULT_REGION` when `base_url` and `AWS_BEDROCK_BASE_URL` are not set
        - `base_url` from `AWS_BEDROCK_BASE_URL`

        `bedrock_token_provider` is invoked before each request when provided. When no bearer token is configured,
        the client uses the standard AWS credential chain and SigV4 authentication.
        """
        if callable(cast(object, api_key)):
            raise OpenAIError("Pass refreshable Bedrock credentials via `bedrock_token_provider`, not `api_key`.")

        if api_key == "":
            raise OpenAIError("The `api_key` argument must not be empty.")

        if api_key is not None and bedrock_token_provider is not None:
            raise OpenAIError(
                "Bedrock authentication is ambiguous. Configure exactly one explicit mode: bearer credential, "
                "static AWS credentials, profile, or credential provider."
            )

        auth_config, aws_auth, api_key, resolved_region = _resolve_bedrock_auth(
            api_key=api_key,
            token_provider=bedrock_token_provider,
            aws_region=aws_region,
            aws_profile=aws_profile,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            aws_credentials_provider=aws_credentials_provider,
            auth_config=_auth_config,
            enforce_credentials=_enforce_credentials,
        )

        self._bedrock_token_provider = bedrock_token_provider
        self._bedrock_auth_config = auth_config
        self._bedrock_aws_auth = aws_auth
        self._uses_region_derived_base_url = (
            _uses_region_derived_bedrock_base_url(base_url)
            if _base_url_is_region_derived is None
            else _base_url_is_region_derived
        )
        self.aws_region = resolved_region

        super().__init__(
            api_key=_bedrock_token_provider(bedrock_token_provider)
            if bedrock_token_provider is not None
            else api_key or "",
            admin_api_key="",
            organization=organization,
            project=project,
            webhook_secret=webhook_secret,
            base_url=_resolve_bedrock_base_url(
                base_url,
                resolved_region,
                use_environment=_base_url_is_region_derived is not True,
            ),
            websocket_base_url=websocket_base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
            _enforce_credentials=False,
        )

    def _uses_aws_auth(self) -> bool:
        return (
            isinstance(self._bedrock_auth_config, _BedrockAwsAuthConfig)
            and not self.api_key
            and self._api_key_provider is None
        )

    @override
    def _auth_headers(self, security: SecurityOptions) -> dict[str, str]:
        if self._uses_aws_auth():
            return {}

        if security.get("bearer_auth", False) or security.get("admin_api_key_auth", False):
            return self._bearer_auth

        return {}

    @override
    def _validate_headers(self, headers: Headers, custom_headers: Headers) -> None:
        if self._uses_aws_auth():
            return

        super()._validate_headers(headers, custom_headers)

    @override
    def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
        if self._uses_aws_auth():
            if options.follow_redirects:
                raise OpenAIError(
                    "Bedrock SigV4 authentication does not support automatic redirects. "
                    "Send a new request to the redirect target so it can be signed again."
                )
            options.follow_redirects = False
        elif (
            self._api_key_provider is not None
            and options.security.get("admin_api_key_auth", False)
            and not options.security.get("bearer_auth", False)
        ):
            self._refresh_api_key()

        return super()._prepare_options(options)

    @override
    def _build_request(self, options: FinalRequestOptions, *, retries_taken: int = 0) -> httpx.Request:
        request = super()._build_request(options, retries_taken=retries_taken)
        if not self._uses_aws_auth():
            return request

        option_headers: Headers = options.headers if is_given(options.headers) else {}
        request.extensions[_BEDROCK_AUTH_INTENT_EXTENSION] = _authorization_intent(
            self._custom_headers,
            option_headers,
        )
        request.extensions[_BEDROCK_MAX_RETRIES_EXTENSION] = options.get_max_retries(self.max_retries)
        return request

    @override
    def _prepare_request(self, request: httpx.Request) -> None:
        if not self._uses_aws_auth():
            return
        if self._bedrock_aws_auth is None:
            assert isinstance(self._bedrock_auth_config, _BedrockAwsAuthConfig)
            self._bedrock_aws_auth = _BedrockAwsAuth(self._bedrock_auth_config)

        intent = request.extensions.get(_BEDROCK_AUTH_INTENT_EXTENSION, _BEDROCK_AUTH_INTENT_DEFAULT)
        if intent == _BEDROCK_AUTH_INTENT_OMIT:
            for header in _AWS_SIGNING_HEADERS:
                request.headers.pop(header, None)
            return
        if intent == _BEDROCK_AUTH_INTENT_OVERRIDE or "Authorization" in request.headers:
            return
        if not _same_origin(request.url, self.base_url):
            raise OpenAIError("Refusing to sign a Bedrock request for an origin other than the configured `base_url`.")

        signed_headers = self._bedrock_aws_auth.sign(
            method=request.method,
            url=str(request.url),
            headers=dict(request.headers),
            body=_body_for_signing(request),
        )
        request.headers.clear()
        request.headers.update(signed_headers)

    @override
    def _send_request(
        self,
        request: httpx.Request,
        *,
        stream: bool,
        **kwargs: Unpack[HttpxSendArgs],
    ) -> httpx.Response:
        if self._uses_aws_auth():
            kwargs["auth"] = httpx.Auth()
        return super()._send_request(request, stream=stream, **kwargs)

    @override
    def copy(
        self,
        *,
        api_key: str | BedrockTokenProvider | None = None,
        admin_api_key: str | None = None,
        workload_identity: WorkloadIdentity | None = None,
        bedrock_token_provider: BedrockTokenProvider | None = None,
        aws_region: str | None = None,
        aws_profile: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        aws_session_token: str | None = None,
        aws_credentials_provider: AwsCredentialsProvider | None = None,
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
            raise OpenAIError("BedrockOpenAI only supports Bedrock bearer token or AWS credential authentication.")

        if api_key is not None and bedrock_token_provider is not None:
            raise OpenAIError(
                "Bedrock authentication is ambiguous. Configure exactly one explicit mode: bearer credential, "
                "static AWS credentials, profile, or credential provider."
            )

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

        aws_auth_override = _has_explicit_aws_auth(
            aws_profile=aws_profile,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            aws_credentials_provider=aws_credentials_provider,
        )
        if (api_key is not None or bedrock_token_provider is not None) and aws_auth_override:
            raise OpenAIError(
                "Bedrock authentication is ambiguous. Configure exactly one explicit mode: bearer credential, "
                "static AWS credentials, profile, or credential provider."
            )
        auth_override = api_key is not None or bedrock_token_provider is not None or aws_auth_override
        if api_key is not None or aws_auth_override:
            next_token_provider = None
        elif bedrock_token_provider is not None:
            next_token_provider = bedrock_token_provider
        else:
            next_token_provider = self._bedrock_token_provider

        next_auth_config: _BedrockBearerAuthConfig | _BedrockAwsAuthConfig | None
        if auth_override:
            next_auth_config = None
        elif isinstance(self._bedrock_auth_config, _BedrockAwsAuthConfig) and self.api_key:
            # The legacy module client allows a module-level API key to replace
            # its construction-time default AWS authentication.
            next_auth_config = None
        elif aws_region is not None:
            if isinstance(self._bedrock_auth_config, _BedrockAwsAuthConfig):
                next_auth_config = replace(
                    self._bedrock_auth_config,
                    region=_resolve_aws_region(aws_region),
                    region_source="explicit",
                )
            else:
                next_auth_config = replace(self._bedrock_auth_config, region_source="explicit")
        else:
            next_auth_config = self._bedrock_auth_config

        next_aws_region = aws_region if aws_region is not None else self.aws_region
        if aws_profile is not None and aws_region is None and self._bedrock_auth_config.region_source != "explicit":
            next_aws_region = None

        next_api_key = api_key
        if next_api_key is None and next_token_provider is None:
            next_api_key = (
                None if aws_auth_override or isinstance(next_auth_config, _BedrockAwsAuthConfig) else self.api_key
            )

        blank_base_url_override = isinstance(base_url, str) and not base_url.strip()
        next_base_url = None if blank_base_url_override else base_url
        next_base_url_is_region_derived = False
        recompute_region_base_url = self._uses_region_derived_base_url and (
            aws_region is not None or (aws_profile is not None and next_aws_region is None)
        )
        if blank_base_url_override:
            next_base_url_is_region_derived = _uses_region_derived_bedrock_base_url(None)
        elif next_base_url is None and not recompute_region_base_url:
            next_base_url = self.base_url
            next_base_url_is_region_derived = self._uses_region_derived_base_url
        elif next_base_url is None and next_aws_region is not None:
            next_base_url = f"https://bedrock-mantle.{next_aws_region}.api.aws/openai/v1"
            next_base_url_is_region_derived = True
        elif next_base_url is None:
            next_base_url_is_region_derived = True

        constructor_kwargs: dict[str, Any] = {
            "api_key": next_api_key,
            "bedrock_token_provider": next_token_provider,
            "aws_region": next_aws_region,
            "organization": organization if organization is not None else self.organization,
            "project": project if project is not None else self.project,
            "webhook_secret": webhook_secret if webhook_secret is not None else self.webhook_secret,
            "websocket_base_url": websocket_base_url if websocket_base_url is not None else self.websocket_base_url,
            "base_url": next_base_url,
            "timeout": self.timeout if isinstance(timeout, NotGiven) else timeout,
            "http_client": http_client or self._client,
            "max_retries": max_retries if is_given(max_retries) else self.max_retries,
            "default_headers": headers,
            "default_query": params,
            "_enforce_credentials": True if _enforce_credentials is None else _enforce_credentials,
            **_extra_kwargs,
        }
        aws_overrides = {
            "aws_profile": aws_profile,
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "aws_session_token": aws_session_token,
            "aws_credentials_provider": aws_credentials_provider,
        }
        constructor_kwargs.update({name: value for name, value in aws_overrides.items() if value is not None})

        supports_auth_config = _constructor_accepts_keyword(self.__class__.__init__, "_auth_config")
        supports_base_url_provenance = _constructor_accepts_keyword(
            self.__class__.__init__, "_base_url_is_region_derived"
        )
        if supports_auth_config:
            constructor_kwargs["_auth_config"] = next_auth_config
        if supports_base_url_provenance:
            constructor_kwargs["_base_url_is_region_derived"] = next_base_url_is_region_derived

        copied = self.__class__(**constructor_kwargs)
        if not supports_auth_config and next_auth_config is not None:
            copied._bedrock_auth_config = next_auth_config
            if isinstance(next_auth_config, _BedrockAwsAuthConfig):
                copied._bedrock_aws_auth = _BedrockAwsAuth(next_auth_config)
                copied._bedrock_token_provider = None
                copied.api_key = ""
                copied._api_key_provider = None
                copied.aws_region = next_auth_config.region
        if not supports_base_url_provenance:
            copied._uses_region_derived_base_url = next_base_url_is_region_derived

        return copied

    with_options = copy


class AsyncBedrockOpenAI(AsyncOpenAI):
    """Async API client for Amazon Bedrock's OpenAI-compatible endpoint."""

    _bedrock_token_provider: AsyncBedrockTokenProvider | None
    _bedrock_auth_config: _BedrockBearerAuthConfig | _BedrockAwsAuthConfig
    _bedrock_aws_auth: _BedrockAwsAuth | None
    _uses_region_derived_base_url: bool
    aws_region: str | None

    def __init__(
        self,
        *,
        api_key: str | None = None,
        bedrock_token_provider: AsyncBedrockTokenProvider | None = None,
        aws_region: str | None = None,
        aws_profile: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        aws_session_token: str | None = None,
        aws_credentials_provider: AwsCredentialsProvider | None = None,
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
        _auth_config: _BedrockBearerAuthConfig | _BedrockAwsAuthConfig | None = None,
        _base_url_is_region_derived: bool | None = None,
    ) -> None:
        """Construct a new asynchronous Amazon Bedrock client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - bearer authentication from `AWS_BEARER_TOKEN_BEDROCK`
        - `aws_region` from `AWS_REGION` or `AWS_DEFAULT_REGION` when `base_url` and `AWS_BEDROCK_BASE_URL` are not set
        - `base_url` from `AWS_BEDROCK_BASE_URL`

        `bedrock_token_provider` is invoked before each request when provided. When no bearer token is configured,
        the client uses the standard AWS credential chain and SigV4 authentication.
        """
        if callable(cast(object, api_key)):
            raise OpenAIError("Pass refreshable Bedrock credentials via `bedrock_token_provider`, not `api_key`.")

        if api_key == "":
            raise OpenAIError("The `api_key` argument must not be empty.")

        if api_key is not None and bedrock_token_provider is not None:
            raise OpenAIError(
                "Bedrock authentication is ambiguous. Configure exactly one explicit mode: bearer credential, "
                "static AWS credentials, profile, or credential provider."
            )

        auth_config, aws_auth, api_key, resolved_region = _resolve_bedrock_auth(
            api_key=api_key,
            token_provider=bedrock_token_provider,
            aws_region=aws_region,
            aws_profile=aws_profile,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            aws_credentials_provider=aws_credentials_provider,
            auth_config=_auth_config,
            enforce_credentials=_enforce_credentials,
        )

        self._bedrock_token_provider = bedrock_token_provider
        self._bedrock_auth_config = auth_config
        self._bedrock_aws_auth = aws_auth
        self._uses_region_derived_base_url = (
            _uses_region_derived_bedrock_base_url(base_url)
            if _base_url_is_region_derived is None
            else _base_url_is_region_derived
        )
        self.aws_region = resolved_region

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
            base_url=_resolve_bedrock_base_url(
                base_url,
                resolved_region,
                use_environment=_base_url_is_region_derived is not True,
            ),
            websocket_base_url=websocket_base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
            _enforce_credentials=False,
        )

    def _uses_aws_auth(self) -> bool:
        return (
            isinstance(self._bedrock_auth_config, _BedrockAwsAuthConfig)
            and not self.api_key
            and self._api_key_provider is None
        )

    @override
    def _auth_headers(self, security: SecurityOptions) -> dict[str, str]:
        if self._uses_aws_auth():
            return {}

        if security.get("bearer_auth", False) or security.get("admin_api_key_auth", False):
            return self._bearer_auth

        return {}

    @override
    def _validate_headers(self, headers: Headers, custom_headers: Headers) -> None:
        if self._uses_aws_auth():
            return

        super()._validate_headers(headers, custom_headers)

    @override
    async def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
        if self._uses_aws_auth():
            if options.follow_redirects:
                raise OpenAIError(
                    "Bedrock SigV4 authentication does not support automatic redirects. "
                    "Send a new request to the redirect target so it can be signed again."
                )
            options.follow_redirects = False
        elif (
            self._api_key_provider is not None
            and options.security.get("admin_api_key_auth", False)
            and not options.security.get("bearer_auth", False)
        ):
            await self._refresh_api_key()

        return await super()._prepare_options(options)

    @override
    def _build_request(self, options: FinalRequestOptions, *, retries_taken: int = 0) -> httpx.Request:
        request = super()._build_request(options, retries_taken=retries_taken)
        if not self._uses_aws_auth():
            return request

        option_headers: Headers = options.headers if is_given(options.headers) else {}
        request.extensions[_BEDROCK_AUTH_INTENT_EXTENSION] = _authorization_intent(
            self._custom_headers,
            option_headers,
        )
        request.extensions[_BEDROCK_MAX_RETRIES_EXTENSION] = options.get_max_retries(self.max_retries)
        return request

    @override
    async def _prepare_request(self, request: httpx.Request) -> None:
        if not self._uses_aws_auth():
            return
        if self._bedrock_aws_auth is None:
            assert isinstance(self._bedrock_auth_config, _BedrockAwsAuthConfig)
            self._bedrock_aws_auth = await asyncify(_BedrockAwsAuth)(self._bedrock_auth_config)

        intent = request.extensions.get(_BEDROCK_AUTH_INTENT_EXTENSION, _BEDROCK_AUTH_INTENT_DEFAULT)
        if intent == _BEDROCK_AUTH_INTENT_OMIT:
            for header in _AWS_SIGNING_HEADERS:
                request.headers.pop(header, None)
            return
        if intent == _BEDROCK_AUTH_INTENT_OVERRIDE or "Authorization" in request.headers:
            return
        if not _same_origin(request.url, self.base_url):
            raise OpenAIError("Refusing to sign a Bedrock request for an origin other than the configured `base_url`.")

        signed_headers = await asyncify(self._bedrock_aws_auth.sign)(
            method=request.method,
            url=str(request.url),
            headers=dict(request.headers),
            body=_body_for_signing(request),
        )
        request.headers.clear()
        request.headers.update(signed_headers)

    @override
    async def _send_request(
        self,
        request: httpx.Request,
        *,
        stream: bool,
        **kwargs: Unpack[HttpxSendArgs],
    ) -> httpx.Response:
        if self._uses_aws_auth():
            kwargs["auth"] = httpx.Auth()
        return await super()._send_request(request, stream=stream, **kwargs)

    @override
    def copy(
        self,
        *,
        api_key: str | AsyncBedrockTokenProvider | None = None,
        admin_api_key: str | None = None,
        workload_identity: WorkloadIdentity | None = None,
        bedrock_token_provider: AsyncBedrockTokenProvider | None = None,
        aws_region: str | None = None,
        aws_profile: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        aws_session_token: str | None = None,
        aws_credentials_provider: AwsCredentialsProvider | None = None,
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
            raise OpenAIError("AsyncBedrockOpenAI only supports Bedrock bearer token or AWS credential authentication.")

        if api_key is not None and bedrock_token_provider is not None:
            raise OpenAIError(
                "Bedrock authentication is ambiguous. Configure exactly one explicit mode: bearer credential, "
                "static AWS credentials, profile, or credential provider."
            )

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

        aws_auth_override = _has_explicit_aws_auth(
            aws_profile=aws_profile,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            aws_credentials_provider=aws_credentials_provider,
        )
        if (api_key is not None or bedrock_token_provider is not None) and aws_auth_override:
            raise OpenAIError(
                "Bedrock authentication is ambiguous. Configure exactly one explicit mode: bearer credential, "
                "static AWS credentials, profile, or credential provider."
            )
        auth_override = api_key is not None or bedrock_token_provider is not None or aws_auth_override
        if api_key is not None or aws_auth_override:
            next_token_provider = None
        elif bedrock_token_provider is not None:
            next_token_provider = bedrock_token_provider
        else:
            next_token_provider = self._bedrock_token_provider

        next_auth_config: _BedrockBearerAuthConfig | _BedrockAwsAuthConfig | None
        if auth_override:
            next_auth_config = None
        elif isinstance(self._bedrock_auth_config, _BedrockAwsAuthConfig) and self.api_key:
            next_auth_config = None
        elif aws_region is not None:
            if isinstance(self._bedrock_auth_config, _BedrockAwsAuthConfig):
                next_auth_config = replace(
                    self._bedrock_auth_config,
                    region=_resolve_aws_region(aws_region),
                    region_source="explicit",
                )
            else:
                next_auth_config = replace(self._bedrock_auth_config, region_source="explicit")
        else:
            next_auth_config = self._bedrock_auth_config

        next_aws_region = aws_region if aws_region is not None else self.aws_region
        if aws_profile is not None and aws_region is None and self._bedrock_auth_config.region_source != "explicit":
            next_aws_region = None

        next_api_key = api_key
        if next_api_key is None and next_token_provider is None:
            next_api_key = (
                None if aws_auth_override or isinstance(next_auth_config, _BedrockAwsAuthConfig) else self.api_key
            )

        blank_base_url_override = isinstance(base_url, str) and not base_url.strip()
        next_base_url = None if blank_base_url_override else base_url
        next_base_url_is_region_derived = False
        recompute_region_base_url = self._uses_region_derived_base_url and (
            aws_region is not None or (aws_profile is not None and next_aws_region is None)
        )
        if blank_base_url_override:
            next_base_url_is_region_derived = _uses_region_derived_bedrock_base_url(None)
        elif next_base_url is None and not recompute_region_base_url:
            next_base_url = self.base_url
            next_base_url_is_region_derived = self._uses_region_derived_base_url
        elif next_base_url is None and next_aws_region is not None:
            next_base_url = f"https://bedrock-mantle.{next_aws_region}.api.aws/openai/v1"
            next_base_url_is_region_derived = True
        elif next_base_url is None:
            next_base_url_is_region_derived = True

        constructor_kwargs: dict[str, Any] = {
            "api_key": next_api_key,
            "bedrock_token_provider": next_token_provider,
            "aws_region": next_aws_region,
            "organization": organization if organization is not None else self.organization,
            "project": project if project is not None else self.project,
            "webhook_secret": webhook_secret if webhook_secret is not None else self.webhook_secret,
            "websocket_base_url": websocket_base_url if websocket_base_url is not None else self.websocket_base_url,
            "base_url": next_base_url,
            "timeout": self.timeout if isinstance(timeout, NotGiven) else timeout,
            "http_client": http_client or self._client,
            "max_retries": max_retries if is_given(max_retries) else self.max_retries,
            "default_headers": headers,
            "default_query": params,
            "_enforce_credentials": True if _enforce_credentials is None else _enforce_credentials,
            **_extra_kwargs,
        }
        aws_overrides = {
            "aws_profile": aws_profile,
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "aws_session_token": aws_session_token,
            "aws_credentials_provider": aws_credentials_provider,
        }
        constructor_kwargs.update({name: value for name, value in aws_overrides.items() if value is not None})

        supports_auth_config = _constructor_accepts_keyword(self.__class__.__init__, "_auth_config")
        supports_base_url_provenance = _constructor_accepts_keyword(
            self.__class__.__init__, "_base_url_is_region_derived"
        )
        if supports_auth_config:
            constructor_kwargs["_auth_config"] = next_auth_config
        if supports_base_url_provenance:
            constructor_kwargs["_base_url_is_region_derived"] = next_base_url_is_region_derived

        copied = self.__class__(**constructor_kwargs)
        if not supports_auth_config and next_auth_config is not None:
            copied._bedrock_auth_config = next_auth_config
            if isinstance(next_auth_config, _BedrockAwsAuthConfig):
                copied._bedrock_aws_auth = _BedrockAwsAuth(next_auth_config)
                copied._bedrock_token_provider = None
                copied.api_key = ""
                copied._api_key_provider = None
                copied.aws_region = next_auth_config.region
        if not supports_base_url_provenance:
            copied._uses_region_derived_base_url = next_base_url_is_region_derived

        return copied

    with_options = copy
