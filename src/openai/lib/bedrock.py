from __future__ import annotations

import os
import re
import inspect
import importlib
from typing import Any, Mapping, Callable, Awaitable, cast
from typing_extensions import Self, override

import httpx

from ..auth import WorkloadIdentity
from .._types import NOT_GIVEN, Headers, Timeout, NotGiven
from .._utils import is_given
from .._client import OpenAI, AsyncOpenAI
from .._models import SecurityOptions, FinalRequestOptions
from .._exceptions import OpenAIError
from .._base_client import DEFAULT_MAX_RETRIES

BedrockTokenProvider = Callable[[], str]
AsyncBedrockTokenProvider = Callable[[], "str | Awaitable[str]"]
AwsCredentialsProvider = Callable[[], object]


class _BedrockAwsBearerAuth:
    def __init__(self) -> None:
        try:
            auth_module = importlib.import_module("botocore.auth")
            awsrequest_module = importlib.import_module("botocore.awsrequest")
            tokens_module = importlib.import_module("botocore.tokens")
        except ImportError:
            self._bearer_auth_cls = None
            self._aws_request_cls = None
            self._frozen_auth_token_cls = None
            return

        self._bearer_auth_cls = auth_module.BearerAuth
        self._aws_request_cls = awsrequest_module.AWSRequest
        self._frozen_auth_token_cls = tokens_module.FrozenAuthToken

    def sign(self, request: httpx.Request, token: str) -> None:
        if self._bearer_auth_cls is None or self._aws_request_cls is None or self._frozen_auth_token_cls is None:
            return

        headers = dict(request.headers)
        headers.pop("authorization", None)
        aws_request = self._aws_request_cls(
            method=request.method,
            url=str(request.url),
            data=request.read(),
            headers=headers,
        )
        self._bearer_auth_cls(self._frozen_auth_token_cls(token)).add_auth(aws_request)
        request.headers.clear()
        request.headers.update(dict(aws_request.headers.items()))


class _BedrockAwsAuth:
    def __init__(
        self,
        *,
        region: str,
        profile: str | None,
        access_key_id: str | None,
        secret_access_key: str | None,
        session_token: str | None,
        credentials_provider: AwsCredentialsProvider | None,
    ) -> None:
        try:
            auth_module = importlib.import_module("botocore.auth")
            session_module = importlib.import_module("botocore.session")
            awsrequest_module = importlib.import_module("botocore.awsrequest")
            credentials_module = importlib.import_module("botocore.credentials")
        except ImportError as exc:
            raise OpenAIError(
                "AWS credential authentication requires botocore. Install it with `pip install openai[bedrock]`."
            ) from exc

        session = session_module.Session(profile=profile)
        service_model = session.get_service_model("bedrock-runtime")
        auth_options = cast("list[str]", service_model.metadata.get("auth", []))
        if auth_module.resolve_auth_scheme_preference(["sigv4"], auth_options) != "v4":
            raise OpenAIError("The installed botocore version does not support Bedrock SigV4 authentication.")

        self._region = region
        self._session = session
        self._credentials_provider = credentials_provider
        self._explicit_credentials = (
            credentials_module.Credentials(access_key_id, secret_access_key, session_token)
            if access_key_id is not None and secret_access_key is not None
            else None
        )
        self._aws_request_cls = awsrequest_module.AWSRequest
        self._sigv4_auth_cls = auth_module.SigV4Auth

    def sign(self, request: httpx.Request) -> None:
        credentials = (
            self._credentials_provider()
            if self._credentials_provider is not None
            else self._explicit_credentials or self._session.get_credentials()
        )
        if credentials is None:
            raise OpenAIError(
                "Could not resolve AWS credentials. Configure the standard AWS credential chain or pass explicit "
                "AWS credentials to the Bedrock client."
            )

        get_frozen_credentials = getattr(credentials, "get_frozen_credentials", None)
        if callable(get_frozen_credentials):
            credentials = get_frozen_credentials()

        headers = dict(request.headers)
        headers.pop("authorization", None)
        aws_request = self._aws_request_cls(
            method=request.method,
            url=str(request.url),
            data=request.read(),
            headers=headers,
        )
        self._sigv4_auth_cls(credentials, "bedrock-mantle", self._region).add_auth(aws_request)
        request.headers.clear()
        request.headers.update(dict(aws_request.headers.items()))


def _has_explicit_aws_auth(
    *,
    aws_profile: str | None,
    aws_access_key_id: str | None,
    aws_secret_access_key: str | None,
    aws_session_token: str | None,
    aws_credentials_provider: AwsCredentialsProvider | None,
) -> bool:
    return any(
        value is not None
        for value in (
            aws_profile,
            aws_access_key_id,
            aws_secret_access_key,
            aws_session_token,
            aws_credentials_provider,
        )
    )


def _validate_explicit_aws_auth(
    *,
    aws_profile: str | None,
    aws_access_key_id: str | None,
    aws_secret_access_key: str | None,
    aws_session_token: str | None,
    aws_credentials_provider: AwsCredentialsProvider | None,
) -> None:
    if (aws_access_key_id is None) != (aws_secret_access_key is None):
        raise OpenAIError("The `aws_access_key_id` and `aws_secret_access_key` arguments must be provided together.")

    credential_sources = sum(
        (
            aws_profile is not None,
            aws_access_key_id is not None,
            aws_credentials_provider is not None,
        )
    )
    if credential_sources > 1:
        raise OpenAIError(
            "The `aws_profile`, explicit AWS credentials, and `aws_credentials_provider` arguments are mutually exclusive."
        )

    if aws_session_token is not None and aws_access_key_id is None:
        raise OpenAIError("The `aws_session_token` argument requires explicit AWS access key credentials.")


def _resolve_aws_region(aws_region: str | None) -> str:
    region = aws_region or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    if region is None or not region.strip():
        raise OpenAIError("AWS credential authentication requires `aws_region`, `AWS_REGION`, or `AWS_DEFAULT_REGION`.")
    return region.strip()


def _resolve_bedrock_env_token() -> str | None:
    if "AWS_BEARER_TOKEN_BEDROCK" not in os.environ:
        return None

    try:
        session_module = importlib.import_module("botocore.session")
    except ImportError:
        return os.environ.get("AWS_BEARER_TOKEN_BEDROCK") or None

    auth_token = session_module.Session().get_auth_token(signing_name="bedrock")
    if auth_token is None:
        return None

    get_frozen_token = getattr(auth_token, "get_frozen_token", None)
    if callable(get_frozen_token):
        auth_token = get_frozen_token()
    token = cast(str, auth_token.token)
    return token or None


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
    _bedrock_aws_bearer_auth: _BedrockAwsBearerAuth | None
    _bedrock_aws_auth: _BedrockAwsAuth | None
    _uses_region_derived_base_url: bool
    _aws_profile: str | None
    _aws_access_key_id: str | None
    _aws_secret_access_key: str | None
    _aws_session_token: str | None
    _aws_credentials_provider: AwsCredentialsProvider | None
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
            raise OpenAIError("The `api_key` and `bedrock_token_provider` arguments are mutually exclusive.")

        explicit_bearer_auth = api_key is not None or bedrock_token_provider is not None
        explicit_aws_auth = _has_explicit_aws_auth(
            aws_profile=aws_profile,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            aws_credentials_provider=aws_credentials_provider,
        )
        if explicit_bearer_auth and explicit_aws_auth:
            raise OpenAIError("Bearer token and AWS credential authentication arguments are mutually exclusive.")

        _validate_explicit_aws_auth(
            aws_profile=aws_profile,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            aws_credentials_provider=aws_credentials_provider,
        )

        if not explicit_bearer_auth and not explicit_aws_auth:
            api_key = _resolve_bedrock_env_token()

        use_aws_auth = api_key is None and bedrock_token_provider is None
        resolved_region = _resolve_aws_region(aws_region) if use_aws_auth else aws_region

        self._bedrock_token_provider = bedrock_token_provider
        self._bedrock_aws_bearer_auth = _BedrockAwsBearerAuth() if not use_aws_auth else None
        self._bedrock_aws_auth = (
            _BedrockAwsAuth(
                region=cast(str, resolved_region),
                profile=aws_profile,
                access_key_id=aws_access_key_id,
                secret_access_key=aws_secret_access_key,
                session_token=aws_session_token,
                credentials_provider=aws_credentials_provider,
            )
            if use_aws_auth and _enforce_credentials
            else None
        )
        self._uses_region_derived_base_url = _uses_region_derived_bedrock_base_url(base_url)
        self._aws_profile = aws_profile
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key
        self._aws_session_token = aws_session_token
        self._aws_credentials_provider = aws_credentials_provider
        self.aws_region = resolved_region

        super().__init__(
            api_key=_bedrock_token_provider(bedrock_token_provider)
            if bedrock_token_provider is not None
            else api_key or "",
            admin_api_key="",
            organization=organization,
            project=project,
            webhook_secret=webhook_secret,
            base_url=_resolve_bedrock_base_url(base_url, resolved_region),
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
        if self._bedrock_aws_auth is not None:
            return {}

        if security.get("bearer_auth", False) or security.get("admin_api_key_auth", False):
            return self._bearer_auth

        return {}

    @override
    def _validate_headers(self, headers: Headers, custom_headers: Headers) -> None:
        if self._bedrock_aws_auth is not None:
            return

        super()._validate_headers(headers, custom_headers)

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
    def _prepare_request(self, request: httpx.Request) -> None:
        if self._bedrock_aws_auth is not None:
            self._bedrock_aws_auth.sign(request)
        elif self._bedrock_aws_bearer_auth is not None:
            self._bedrock_aws_bearer_auth.sign(request, self.api_key)

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

        aws_auth_override = _has_explicit_aws_auth(
            aws_profile=aws_profile,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            aws_credentials_provider=aws_credentials_provider,
        )
        if api_key is not None or aws_auth_override:
            next_token_provider = None
        elif bedrock_token_provider is not None:
            next_token_provider = bedrock_token_provider
        else:
            next_token_provider = self._bedrock_token_provider

        preserve_aws_auth = (
            self._bedrock_aws_auth is not None
            and not aws_auth_override
            and api_key is None
            and next_token_provider is None
        )
        next_api_key = (
            api_key
            if api_key is not None
            else None
            if next_token_provider is not None or preserve_aws_auth or aws_auth_override
            else self.api_key
        )
        next_base_url = base_url
        if next_base_url is None and not (aws_region is not None and self._uses_region_derived_base_url):
            next_base_url = self.base_url

        return self.__class__(
            api_key=next_api_key,
            bedrock_token_provider=next_token_provider,
            aws_region=aws_region if aws_region is not None else self.aws_region,
            aws_profile=aws_profile if aws_profile is not None else self._aws_profile if preserve_aws_auth else None,
            aws_access_key_id=(
                aws_access_key_id
                if aws_access_key_id is not None
                else self._aws_access_key_id
                if preserve_aws_auth
                else None
            ),
            aws_secret_access_key=(
                aws_secret_access_key
                if aws_secret_access_key is not None
                else self._aws_secret_access_key
                if preserve_aws_auth
                else None
            ),
            aws_session_token=(
                aws_session_token
                if aws_session_token is not None
                else self._aws_session_token
                if preserve_aws_auth
                else None
            ),
            aws_credentials_provider=(
                aws_credentials_provider
                if aws_credentials_provider is not None
                else self._aws_credentials_provider
                if preserve_aws_auth
                else None
            ),
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
    _bedrock_aws_bearer_auth: _BedrockAwsBearerAuth | None
    _bedrock_aws_auth: _BedrockAwsAuth | None
    _uses_region_derived_base_url: bool
    _aws_profile: str | None
    _aws_access_key_id: str | None
    _aws_secret_access_key: str | None
    _aws_session_token: str | None
    _aws_credentials_provider: AwsCredentialsProvider | None
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
            raise OpenAIError("The `api_key` and `bedrock_token_provider` arguments are mutually exclusive.")

        explicit_bearer_auth = api_key is not None or bedrock_token_provider is not None
        explicit_aws_auth = _has_explicit_aws_auth(
            aws_profile=aws_profile,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            aws_credentials_provider=aws_credentials_provider,
        )
        if explicit_bearer_auth and explicit_aws_auth:
            raise OpenAIError("Bearer token and AWS credential authentication arguments are mutually exclusive.")

        _validate_explicit_aws_auth(
            aws_profile=aws_profile,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            aws_credentials_provider=aws_credentials_provider,
        )

        if not explicit_bearer_auth and not explicit_aws_auth:
            api_key = _resolve_bedrock_env_token()

        use_aws_auth = api_key is None and bedrock_token_provider is None
        resolved_region = _resolve_aws_region(aws_region) if use_aws_auth else aws_region

        self._bedrock_token_provider = bedrock_token_provider
        self._bedrock_aws_bearer_auth = _BedrockAwsBearerAuth() if not use_aws_auth else None
        self._bedrock_aws_auth = (
            _BedrockAwsAuth(
                region=cast(str, resolved_region),
                profile=aws_profile,
                access_key_id=aws_access_key_id,
                secret_access_key=aws_secret_access_key,
                session_token=aws_session_token,
                credentials_provider=aws_credentials_provider,
            )
            if use_aws_auth and _enforce_credentials
            else None
        )
        self._uses_region_derived_base_url = _uses_region_derived_bedrock_base_url(base_url)
        self._aws_profile = aws_profile
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key
        self._aws_session_token = aws_session_token
        self._aws_credentials_provider = aws_credentials_provider
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
            base_url=_resolve_bedrock_base_url(base_url, resolved_region),
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
        if self._bedrock_aws_auth is not None:
            return {}

        if security.get("bearer_auth", False) or security.get("admin_api_key_auth", False):
            return self._bearer_auth

        return {}

    @override
    def _validate_headers(self, headers: Headers, custom_headers: Headers) -> None:
        if self._bedrock_aws_auth is not None:
            return

        super()._validate_headers(headers, custom_headers)

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
    async def _prepare_request(self, request: httpx.Request) -> None:
        if self._bedrock_aws_auth is not None:
            self._bedrock_aws_auth.sign(request)
        elif self._bedrock_aws_bearer_auth is not None:
            self._bedrock_aws_bearer_auth.sign(request, self.api_key)

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

        aws_auth_override = _has_explicit_aws_auth(
            aws_profile=aws_profile,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            aws_credentials_provider=aws_credentials_provider,
        )
        if api_key is not None or aws_auth_override:
            next_token_provider = None
        elif bedrock_token_provider is not None:
            next_token_provider = bedrock_token_provider
        else:
            next_token_provider = self._bedrock_token_provider

        preserve_aws_auth = (
            self._bedrock_aws_auth is not None
            and not aws_auth_override
            and api_key is None
            and next_token_provider is None
        )
        next_api_key = (
            api_key
            if api_key is not None
            else None
            if next_token_provider is not None or preserve_aws_auth or aws_auth_override
            else self.api_key
        )
        next_base_url = base_url
        if next_base_url is None and not (aws_region is not None and self._uses_region_derived_base_url):
            next_base_url = self.base_url

        return self.__class__(
            api_key=next_api_key,
            bedrock_token_provider=next_token_provider,
            aws_region=aws_region if aws_region is not None else self.aws_region,
            aws_profile=aws_profile if aws_profile is not None else self._aws_profile if preserve_aws_auth else None,
            aws_access_key_id=(
                aws_access_key_id
                if aws_access_key_id is not None
                else self._aws_access_key_id
                if preserve_aws_auth
                else None
            ),
            aws_secret_access_key=(
                aws_secret_access_key
                if aws_secret_access_key is not None
                else self._aws_secret_access_key
                if preserve_aws_auth
                else None
            ),
            aws_session_token=(
                aws_session_token
                if aws_session_token is not None
                else self._aws_session_token
                if preserve_aws_auth
                else None
            ),
            aws_credentials_provider=(
                aws_credentials_provider
                if aws_credentials_provider is not None
                else self._aws_credentials_provider
                if preserve_aws_auth
                else None
            ),
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
