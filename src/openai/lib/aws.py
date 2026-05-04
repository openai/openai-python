from __future__ import annotations

import os
import inspect
from typing import Any, Union, Mapping, Callable, Awaitable
from typing_extensions import Self, override

import httpx

from .._types import NOT_GIVEN, Timeout, NotGiven
from .._client import OpenAI, AsyncOpenAI
from .._exceptions import OpenAIError
from .._base_client import DEFAULT_MAX_RETRIES

# Sentinel API key used when SigV4 mode is active, so the base OpenAI
# constructor (which requires a non-None api_key) is satisfied.
API_KEY_SENTINEL = "<bedrock-mantle-sigv4>"

# A credential provider is a callable that returns a botocore-compatible
# credentials object (with access_key, secret_key, token attributes).
CredentialProvider = Callable[[], Any]
AsyncCredentialProvider = Callable[[], "Union[Any, Awaitable[Any]]"]


def _ensure_botocore() -> None:
    """Raise OpenAIError if botocore is not installed."""
    try:
        import botocore  # type: ignore[import-untyped]  # noqa: F401  # pyright: ignore[reportMissingTypeStubs, reportUnusedImport]
    except ImportError as err:
        raise OpenAIError(
            "botocore must be installed for SigV4 authentication. Install it with: pip install 'openai[aws]'"
        ) from err


def _get_default_credentials() -> Any:
    """Resolve the botocore credentials object via the default credential chain.

    Returns the unfrozen botocore credentials object so that RefreshableCredentials
    (e.g. from IAM roles, EC2 instance profiles, ECS task roles) can auto-refresh
    on subsequent access. Raises OpenAIError if botocore is not installed or
    credentials cannot be resolved.
    """
    _ensure_botocore()
    import botocore.session  # type: ignore[import-untyped]  # pyright: ignore[reportMissingTypeStubs]

    session = botocore.session.get_session()  # pyright: ignore[reportUnknownMemberType]
    creds = session.get_credentials()  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
    if creds is None:
        raise OpenAIError("Could not resolve AWS credentials from the default botocore credential chain.")
    # Validate that credentials are usable by checking a frozen snapshot,
    # but return the unfrozen object so RefreshableCredentials can auto-refresh.
    frozen = creds.get_frozen_credentials()  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
    if not frozen.access_key or not frozen.secret_key:  # pyright: ignore[reportUnknownMemberType]
        raise OpenAIError("Could not resolve AWS credentials from the default botocore credential chain.")
    return creds  # pyright: ignore[reportUnknownVariableType]


def _sign_httpx_request(
    request: httpx.Request,
    credentials: Any,
    region: str,
    service: str = "bedrock",
) -> None:
    """Sign an httpx.Request in-place using botocore's SigV4Auth."""
    import botocore.auth  # type: ignore[import-untyped]  # pyright: ignore[reportMissingTypeStubs]
    import botocore.awsrequest  # type: ignore[import-untyped]  # pyright: ignore[reportMissingTypeStubs]

    # Exclude httpx transport-level headers that cause SigV4 signature mismatch
    _HEADERS_TO_EXCLUDE = {"connection", "accept-encoding"}
    clean_headers = {k: v for k, v in request.headers.items() if k.lower() not in _HEADERS_TO_EXCLUDE}

    # Convert httpx.Request → botocore.awsrequest.AWSRequest
    aws_request = botocore.awsrequest.AWSRequest(
        method=request.method,
        url=str(request.url),
        headers=clean_headers,
        data=request.content,
    )

    signer = botocore.auth.SigV4Auth(credentials, service, region)
    signer.add_auth(aws_request)  # pyright: ignore[reportUnknownMemberType]

    # Copy signed headers back into the httpx request
    for key, value in aws_request.headers.items():
        request.headers[key] = value


# ---------------------------------------------------------------------------
# Shared init / credential resolution logic
# ---------------------------------------------------------------------------


def _resolve_bedrock_mantle_config(
    *,
    api_key: str | None,
    credential_provider: Any | None,
    region: str | None,
    base_url: str | None,
) -> tuple[bool, Any | None, str, str, Any | None]:
    """Shared constructor logic for both sync and async clients.

    Returns (use_sigv4, credential_provider, region, base_url, botocore_credentials).
    """
    # Normalize: treat the sentinel as "no api_key provided"
    if api_key == API_KEY_SENTINEL:
        api_key = None

    if api_key is not None and credential_provider is not None:
        raise OpenAIError("api_key and credential_provider are mutually exclusive")

    # Determine auth mode
    if api_key is not None:
        use_sigv4 = False
        credential_provider = None
    else:
        use_sigv4 = True

    # Resolve region (needed for SigV4 and base_url fallback)
    resolved_region = region or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    if use_sigv4 and not resolved_region:
        raise ValueError("Must provide region or set AWS_REGION / AWS_DEFAULT_REGION environment variable")
    resolved_region = resolved_region or ""

    # Resolve base_url — fall back to region-derived endpoint
    if base_url is None:
        if not resolved_region:
            raise ValueError("Must provide base_url, or set region / AWS_REGION / AWS_DEFAULT_REGION")
        base_url = f"https://bedrock-mantle.{resolved_region}.api.aws/v1"

    # Resolve botocore credentials if needed
    botocore_credentials: Any = None
    if use_sigv4 and credential_provider is None:
        botocore_credentials = _get_default_credentials()
    elif use_sigv4:
        # SigV4 signing always requires botocore (for botocore.auth.SigV4Auth)
        _ensure_botocore()

    return use_sigv4, credential_provider, resolved_region, base_url, botocore_credentials


def _resolve_credentials_sync(
    credential_provider: CredentialProvider | None,
    botocore_credentials: Any | None,
) -> Any:
    """Resolve credentials for a sync request. Raises OpenAIError on failure."""
    try:
        if credential_provider is not None:
            return credential_provider()
        # Call get_frozen_credentials() at signing time so that
        # RefreshableCredentials can auto-refresh expired tokens.
        if botocore_credentials is not None and hasattr(botocore_credentials, "get_frozen_credentials"):
            return botocore_credentials.get_frozen_credentials()  # pyright: ignore[reportUnknownMemberType]
        return botocore_credentials
    except OpenAIError:
        raise
    except Exception as e:
        raise OpenAIError(f"Failed to refresh AWS credentials: {e}") from e


async def _resolve_credentials_async(
    credential_provider: AsyncCredentialProvider | None,
    botocore_credentials: Any | None,
) -> Any:
    """Resolve credentials for an async request. Raises OpenAIError on failure."""
    try:
        if credential_provider is not None:
            credentials = credential_provider()
            if inspect.isawaitable(credentials):
                credentials = await credentials
            return credentials
        # Call get_frozen_credentials() at signing time so that
        # RefreshableCredentials can auto-refresh expired tokens.
        if botocore_credentials is not None and hasattr(botocore_credentials, "get_frozen_credentials"):
            return botocore_credentials.get_frozen_credentials()  # pyright: ignore[reportUnknownMemberType]
        return botocore_credentials
    except OpenAIError:
        raise
    except Exception as e:
        raise OpenAIError(f"Failed to refresh AWS credentials: {e}") from e


# ---------------------------------------------------------------------------
# Client classes
# ---------------------------------------------------------------------------


class AwsOpenAI(OpenAI):
    """OpenAI-compatible client for AWS Bedrock Mantle APIs.

    Supports SigV4 request signing and API key authentication.
    """

    _region: str
    _credential_provider: CredentialProvider | None
    _use_sigv4: bool
    _botocore_credentials: Any

    def __init__(
        self,
        *,
        base_url: str | None = None,
        region: str | None = None,
        credential_provider: CredentialProvider | None = None,
        api_key: str | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.Client | None = None,
        _strict_response_validation: bool = False,
        **kwargs: Any,
    ) -> None:
        (
            self._use_sigv4,
            self._credential_provider,
            self._region,
            base_url,
            self._botocore_credentials,
        ) = _resolve_bedrock_mantle_config(
            api_key=api_key,
            credential_provider=credential_provider,
            region=region,
            base_url=base_url,
        )

        super().__init__(
            api_key=api_key or API_KEY_SENTINEL,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
            **kwargs,
        )

    @override
    def _prepare_request(self, request: httpx.Request) -> None:
        if not self._use_sigv4:
            return
        credentials = _resolve_credentials_sync(self._credential_provider, self._botocore_credentials)
        _sign_httpx_request(request, credentials, self._region)

    @override
    def copy(
        self,
        *,
        region: str | None = None,
        credential_provider: CredentialProvider | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
        **kwargs: Any,
    ) -> Self:
        """Create a new client instance re-using the same options given to the current client with optional overriding."""
        return super().copy(
            **kwargs,
            _extra_kwargs={
                "region": region or self._region,
                "credential_provider": credential_provider or self._credential_provider,
                **_extra_kwargs,
            },
        )

    with_options = copy


class AsyncAwsOpenAI(AsyncOpenAI):
    """Async OpenAI-compatible client for AWS Bedrock Mantle APIs.

    Supports SigV4 request signing and API key authentication.
    """

    _region: str
    _credential_provider: AsyncCredentialProvider | None
    _use_sigv4: bool
    _botocore_credentials: Any

    def __init__(
        self,
        *,
        base_url: str | None = None,
        region: str | None = None,
        credential_provider: AsyncCredentialProvider | None = None,
        api_key: str | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.AsyncClient | None = None,
        _strict_response_validation: bool = False,
        **kwargs: Any,
    ) -> None:
        (
            self._use_sigv4,
            self._credential_provider,
            self._region,
            base_url,
            self._botocore_credentials,
        ) = _resolve_bedrock_mantle_config(
            api_key=api_key,
            credential_provider=credential_provider,
            region=region,
            base_url=base_url,
        )

        super().__init__(
            api_key=api_key or API_KEY_SENTINEL,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
            **kwargs,
        )

    @override
    async def _prepare_request(self, request: httpx.Request) -> None:
        if not self._use_sigv4:
            return
        credentials = await _resolve_credentials_async(self._credential_provider, self._botocore_credentials)
        _sign_httpx_request(request, credentials, self._region)

    @override
    def copy(
        self,
        *,
        region: str | None = None,
        credential_provider: AsyncCredentialProvider | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
        **kwargs: Any,
    ) -> Self:
        """Create a new client instance re-using the same options given to the current client with optional overriding."""
        return super().copy(
            **kwargs,
            _extra_kwargs={
                "region": region or self._region,
                "credential_provider": credential_provider or self._credential_provider,
                **_extra_kwargs,
            },
        )

    with_options = copy

