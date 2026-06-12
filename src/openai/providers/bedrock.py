from __future__ import annotations

import os
import re
import inspect
from typing import Literal, Callable, Awaitable, cast
from dataclasses import field, dataclass

import httpx

from .._types import NOT_GIVEN, NotGiven
from .._utils import asyncify
from .._models import FinalRequestOptions
from .._provider import _Provider, _create_provider, _ProviderRuntime
from .._exceptions import OpenAIError
from ..lib._bedrock_auth import (
    BedrockAwsAuth,
    BedrockAwsAuthConfig,
    AwsCredentialsProvider,
)

BedrockTokenProvider = Callable[[], "str | Awaitable[str]"]

_AWS_SIGNING_HEADERS = ("authorization", "x-amz-content-sha256", "x-amz-date", "x-amz-security-token")
_CANONICAL_BEDROCK_HOST = re.compile(r"^bedrock-mantle\.([a-z0-9-]+)\.api\.aws$", re.IGNORECASE)


def _normalize_optional_string(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    return normalized or None


def _normalize_base_url(base_url: str | httpx.URL) -> httpx.URL:
    url = httpx.URL(base_url)
    path = url.path.rstrip("/")
    responses_match = re.search(r"/responses(?:/.*)?$", path)
    if responses_match is not None:
        path = path[: responses_match.start()]

    return url.copy_with(path=path or "/")


def _same_origin(left: httpx.URL, right: httpx.URL) -> bool:
    return (left.scheme, left.host, left.port) == (right.scheme, right.host, right.port)


def _body_for_signing(request: httpx.Request) -> bytes:
    try:
        return request.content
    except httpx.RequestNotRead as exc:
        raise OpenAIError(
            "Bedrock SigV4 authentication requires a replayable request body. "
            "Buffer the body before sending or use bearer authentication."
        ) from exc


def _assert_provider_owns_authorization(request: httpx.Request) -> None:
    if "Authorization" in request.headers:
        raise OpenAIError("Bedrock provider authentication cannot be combined with a custom `Authorization` header.")


def _without_redirects(options: FinalRequestOptions) -> FinalRequestOptions:
    if options.follow_redirects:
        raise OpenAIError(
            "Bedrock SigV4 authentication does not support automatic redirects. "
            "Send a new request to the redirect target so it can be signed again."
        )
    options.follow_redirects = False
    return options


class _BedrockBearerAuth:
    def __init__(self, token_provider: BedrockTokenProvider, *, base_url: httpx.URL) -> None:
        self._token_provider = token_provider
        self._base_url = base_url

    def _validate_request(self, request: httpx.Request) -> None:
        _assert_provider_owns_authorization(request)
        if not _same_origin(request.url, self._base_url):
            raise OpenAIError(
                "Refusing to authenticate a Bedrock request for an origin other than the configured provider URL."
            )

    def _resolve_token(self) -> str:
        try:
            token = cast(object, self._token_provider())
        except OpenAIError:
            raise
        except Exception as exc:
            raise OpenAIError("Failed to resolve a bearer credential for Bedrock.") from exc

        if inspect.isawaitable(token):
            close = getattr(token, "close", None)
            if callable(close):
                close()
            raise OpenAIError("An async Bedrock token provider requires `AsyncOpenAI`.")
        if not isinstance(token, str) or not token.strip():
            raise OpenAIError("The Bedrock bearer credential provider must return a non-empty string.")
        return token

    async def _resolve_token_async(self) -> str:
        try:
            token = cast(object, self._token_provider())
            if inspect.isawaitable(token):
                token = await token
        except OpenAIError:
            raise
        except Exception as exc:
            raise OpenAIError("Failed to resolve a bearer credential for Bedrock.") from exc

        if not isinstance(token, str) or not token.strip():
            raise OpenAIError("The Bedrock bearer credential provider must return a non-empty string.")
        return token

    def prepare_request(self, request: httpx.Request) -> None:
        self._validate_request(request)
        request.headers["Authorization"] = f"Bearer {self._resolve_token()}"

    async def prepare_async_request(self, request: httpx.Request) -> None:
        self._validate_request(request)
        request.headers["Authorization"] = f"Bearer {await self._resolve_token_async()}"


class _BedrockSigV4Auth:
    def __init__(
        self,
        *,
        config: BedrockAwsAuthConfig,
        base_url: httpx.URL,
        auth: BedrockAwsAuth | None = None,
    ) -> None:
        self._config = config
        self._base_url = base_url
        self._auth = auth

    def _validate_request(self, request: httpx.Request) -> bytes:
        _assert_provider_owns_authorization(request)
        if not _same_origin(request.url, self._base_url):
            raise OpenAIError(
                "Refusing to sign a Bedrock request for an origin other than the configured provider URL."
            )

        endpoint_region_match = _CANONICAL_BEDROCK_HOST.fullmatch(request.url.host)
        if endpoint_region_match is not None and endpoint_region_match.group(1) != self._config.region:
            raise OpenAIError(
                f"The Bedrock endpoint region `{endpoint_region_match.group(1)}` does not match the "
                f"SigV4 region `{self._config.region}`."
            )

        return _body_for_signing(request)

    def _sign(self, request: httpx.Request, *, auth: BedrockAwsAuth, body: bytes) -> None:
        for header in _AWS_SIGNING_HEADERS:
            request.headers.pop(header, None)

        signed_headers = auth.sign(
            method=request.method,
            url=str(request.url),
            headers=dict(request.headers),
            body=body,
        )
        request.headers.clear()
        request.headers.update(signed_headers)

    def prepare_request(self, request: httpx.Request) -> None:
        body = self._validate_request(request)
        if self._auth is None:
            self._auth = BedrockAwsAuth(self._config)
        self._sign(request, auth=self._auth, body=body)

    async def prepare_async_request(self, request: httpx.Request) -> None:
        body = self._validate_request(request)
        if self._auth is None:
            self._auth = await asyncify(BedrockAwsAuth)(self._config)

        signed_headers = await asyncify(self._auth.sign)(
            method=request.method,
            url=str(request.url),
            headers={
                name: value for name, value in request.headers.items() if name.lower() not in _AWS_SIGNING_HEADERS
            },
            body=body,
        )
        request.headers.clear()
        request.headers.update(signed_headers)


@dataclass(frozen=True)
class _BedrockProviderDefinition:
    configured_region: str | None
    region_source: Literal["explicit", "environment"] | None
    configured_base_url: httpx.URL | None
    api_key: str | None = field(default=None, repr=False)
    token_provider: BedrockTokenProvider | None = field(default=None, repr=False, compare=False)
    use_environment_bearer: bool = False
    profile: str | None = None
    access_key_id: str | None = field(default=None, repr=False)
    secret_access_key: str | None = field(default=None, repr=False)
    session_token: str | None = field(default=None, repr=False)
    credential_provider: AwsCredentialsProvider | None = field(default=None, repr=False, compare=False)
    name: str = field(default="bedrock", init=False)

    def _aws_source(self) -> Literal["static", "profile", "provider", "default"]:
        if self.access_key_id is not None:
            return "static"
        if self.profile is not None:
            return "profile"
        if self.credential_provider is not None:
            return "provider"
        return "default"

    def _resolve_aws_auth(self) -> tuple[BedrockAwsAuthConfig, BedrockAwsAuth | None]:
        if self.configured_region is not None:
            return (
                BedrockAwsAuthConfig(
                    region=self.configured_region,
                    source=self._aws_source(),
                    region_source=self.region_source or "explicit",
                    profile=self.profile,
                    access_key_id=self.access_key_id,
                    secret_access_key=self.secret_access_key,
                    session_token=self.session_token,
                    credentials_provider=self.credential_provider,
                ),
                None,
            )

        auth = BedrockAwsAuth.resolve(
            region=None,
            profile=self.profile,
            access_key_id=self.access_key_id,
            secret_access_key=self.secret_access_key,
            session_token=self.session_token,
            credentials_provider=self.credential_provider,
        )
        return auth.config, auth

    def configure(self) -> _ProviderRuntime:
        def environment_token() -> str:
            token = os.environ.get("AWS_BEARER_TOKEN_BEDROCK")
            if not token:
                raise OpenAIError(
                    "Could not find credentials for Bedrock. Pass a bearer credential or AWS credentials to "
                    "`bedrock(...)`, set `AWS_BEARER_TOKEN_BEDROCK`, or configure the default AWS credential chain."
                )
            return token

        auth: _BedrockBearerAuth | _BedrockSigV4Auth | None = None
        bearer_provider: BedrockTokenProvider | None = None
        if self.api_key is not None:
            bearer_provider = lambda: self.api_key or ""
            region = self.configured_region
        elif self.token_provider is not None:
            bearer_provider = self.token_provider
            region = self.configured_region
        elif self.use_environment_bearer:
            bearer_provider = environment_token
            region = self.configured_region
        else:
            aws_config, aws_auth = self._resolve_aws_auth()
            region = aws_config.region
            base_url = self.configured_base_url or _normalize_base_url(
                f"https://bedrock-mantle.{region}.api.aws/openai/v1"
            )
            auth = _BedrockSigV4Auth(config=aws_config, base_url=base_url, auth=aws_auth)

        if self.configured_base_url is not None:
            base_url = self.configured_base_url
        elif region is not None:
            base_url = _normalize_base_url(f"https://bedrock-mantle.{region}.api.aws/openai/v1")
        else:
            raise OpenAIError(
                "Bedrock requires an AWS region. Pass `region` to `bedrock(...)`, or set `AWS_REGION` or "
                "`AWS_DEFAULT_REGION`."
            )

        if bearer_provider is not None:
            auth = _BedrockBearerAuth(bearer_provider, base_url=base_url)

        assert auth is not None
        if isinstance(auth, _BedrockSigV4Auth):
            return _ProviderRuntime(
                name=self.name,
                base_url=base_url,
                transform_request=_without_redirects,
                prepare_request=auth.prepare_request,
                prepare_async_request=auth.prepare_async_request,
            )

        return _ProviderRuntime(
            name=self.name,
            base_url=base_url,
            prepare_request=auth.prepare_request,
            prepare_async_request=auth.prepare_async_request,
        )


def bedrock(
    *,
    region: str | None = None,
    base_url: str | httpx.URL | None | NotGiven = NOT_GIVEN,
    api_key: str | None | NotGiven = NOT_GIVEN,
    token_provider: BedrockTokenProvider | None = None,
    access_key_id: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
    profile: str | None = None,
    credential_provider: AwsCredentialsProvider | None = None,
) -> _Provider:
    """Configure the standard OpenAI client for Amazon Bedrock Mantle."""

    normalized_region = _normalize_optional_string(region)
    if region is not None and normalized_region is None:
        raise OpenAIError("The Bedrock AWS `region` must not be empty.")

    region_source: Literal["explicit", "environment"] | None = None
    if normalized_region is not None:
        region_source = "explicit"
    else:
        normalized_region = _normalize_optional_string(
            os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
        )
        if normalized_region is not None:
            region_source = "environment"

    configured_base_url: httpx.URL | None
    if isinstance(base_url, NotGiven):
        environment_base_url = _normalize_optional_string(os.environ.get("AWS_BEDROCK_BASE_URL"))
        configured_base_url = _normalize_base_url(environment_base_url) if environment_base_url else None
    elif base_url is None:
        configured_base_url = None
    else:
        if isinstance(base_url, str) and not base_url.strip():
            raise OpenAIError("The Bedrock `base_url` must not be empty.")
        configured_base_url = _normalize_base_url(base_url)

    normalized_profile = _normalize_optional_string(profile)
    if profile is not None and normalized_profile is None:
        raise OpenAIError("The Bedrock AWS `profile` must not be empty.")

    if (access_key_id is None) != (secret_access_key is None) or (session_token is not None and access_key_id is None):
        raise OpenAIError(
            "Static AWS credentials require both `access_key_id` and `secret_access_key`. "
            "A `session_token` may only be used with both."
        )
    if access_key_id is not None and (not access_key_id.strip() or not cast(str, secret_access_key).strip()):
        raise OpenAIError("Static AWS credentials require non-empty `access_key_id` and `secret_access_key` values.")
    if session_token is not None and not session_token.strip():
        raise OpenAIError("A static AWS `session_token` must not be empty when provided.")

    explicit_api_key = not isinstance(api_key, NotGiven) and api_key is not None
    if explicit_api_key and (not isinstance(api_key, str) or not api_key.strip()):
        raise OpenAIError("The Bedrock bearer credential must not be empty.")
    if explicit_api_key and token_provider is not None:
        raise OpenAIError("The `api_key` and `token_provider` options are mutually exclusive. Configure only one.")

    explicit_bearer = explicit_api_key or token_provider is not None
    aws_modes = sum(
        (
            access_key_id is not None,
            normalized_profile is not None,
            credential_provider is not None,
        )
    )
    if aws_modes > 1:
        raise OpenAIError(
            "Bedrock authentication is ambiguous. Configure exactly one explicit AWS mode: static credentials, "
            "profile, or credential provider."
        )
    if explicit_bearer and aws_modes:
        raise OpenAIError(
            "Bedrock authentication is ambiguous. Configure exactly one explicit mode: bearer credential, "
            "static AWS credentials, profile, or credential provider."
        )

    skip_environment_bearer = not isinstance(api_key, NotGiven) and api_key is None
    use_environment_bearer = (
        not explicit_bearer
        and not aws_modes
        and not skip_environment_bearer
        and bool(os.environ.get("AWS_BEARER_TOKEN_BEDROCK"))
    )

    return _create_provider(
        _BedrockProviderDefinition(
            configured_region=normalized_region,
            region_source=region_source,
            configured_base_url=configured_base_url,
            api_key=cast("str | None", api_key) if explicit_api_key else None,
            token_provider=token_provider,
            use_environment_bearer=use_environment_bearer,
            profile=normalized_profile,
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            session_token=session_token,
            credential_provider=credential_provider,
        )
    )


__all__ = ["bedrock", "BedrockTokenProvider", "AwsCredentialsProvider"]
