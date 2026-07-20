from __future__ import annotations

import os
import re
import hmac
import inspect
from typing import Any, Literal, Mapping, Callable, Optional, Awaitable, cast
from dataclasses import field, replace, dataclass
from typing_extensions import Self, override

import httpx

from ..auth import WorkloadIdentity
from .._types import NOT_GIVEN, Timeout, NotGiven
from .._utils import is_given
from .._client import OpenAI, AsyncOpenAI
from .._models import FinalRequestOptions
from .._provider import _Provider, _configure_provider
from .._exceptions import OpenAIError
from .._base_client import DEFAULT_MAX_RETRIES
from ..providers.bedrock import AwsCredentialsProvider, bedrock, _BedrockProviderRuntime

BedrockTokenProvider = Callable[[], str]
AsyncBedrockTokenProvider = Callable[[], "str | Awaitable[str]"]
_LegacyAuthMode = Literal["bearer", "token_provider", "aws"]
_LegacyAuthConfiguration = tuple[_LegacyAuthMode, Optional[object]]
_LEGACY_SIGNATURE_NONCE = os.urandom(32)


@dataclass(frozen=True)
class _LegacyRuntimeSignature:
    mode: _LegacyAuthMode
    base_url: str
    region: str | None
    credential_identity: object = field(repr=False)


@dataclass(frozen=True)
class _LegacyBedrockState:
    explicit_api_key: str | None = field(repr=False)
    token_provider: BedrockTokenProvider | AsyncBedrockTokenProvider | None = field(repr=False, compare=False)
    aws_region: str | None
    region_was_explicit: bool
    aws_profile: str | None
    aws_access_key_id: str | None = field(repr=False)
    aws_secret_access_key: str | None = field(repr=False)
    aws_session_token: str | None = field(repr=False)
    aws_credentials_provider: AwsCredentialsProvider | None = field(repr=False, compare=False)
    uses_environment_bearer: bool
    environment_bearer_token: str | None = field(repr=False)
    uses_region_derived_base_url: bool


def _state_api_key(state: _LegacyBedrockState) -> str:
    return state.explicit_api_key or (state.environment_bearer_token if state.uses_environment_bearer else "") or ""


def _constructor_accepts_keyword(constructor: Callable[..., object], name: str) -> bool:
    try:
        parameters = inspect.signature(constructor).parameters
    except (TypeError, ValueError):
        return False

    return name in parameters or any(
        parameter.kind is inspect.Parameter.VAR_KEYWORD for parameter in parameters.values()
    )


def _configured_region(region: str | None) -> str | None:
    configured = region or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    return configured.strip() if configured is not None and configured.strip() else None


def _uses_region_derived_base_url(base_url: str | httpx.URL | None) -> bool:
    if isinstance(base_url, str) and not base_url.strip():
        base_url = None
    if base_url is not None:
        return False

    environment_base_url = os.environ.get("AWS_BEDROCK_BASE_URL")
    return environment_base_url is None or not environment_base_url.strip()


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


def _environment_bearer_token() -> str:
    token = os.environ.get("AWS_BEARER_TOKEN_BEDROCK")
    if not token:
        raise OpenAIError(
            "Could not find credentials for Bedrock. Set `AWS_BEARER_TOKEN_BEDROCK` or configure the default "
            "AWS credential chain."
        )
    return token


def _legacy_provider(
    *,
    api_key: str | None,
    token_provider: BedrockTokenProvider | AsyncBedrockTokenProvider | None,
    aws_region: str | None,
    aws_profile: str | None,
    aws_access_key_id: str | None,
    aws_secret_access_key: str | None,
    aws_session_token: str | None,
    aws_credentials_provider: AwsCredentialsProvider | None,
    base_url: str | httpx.URL | None,
    region_was_explicit: bool | None = None,
) -> tuple[_Provider, _LegacyBedrockState, str]:
    if callable(cast(object, api_key)):
        raise OpenAIError("Pass refreshable Bedrock credentials via `bedrock_token_provider`, not `api_key`.")
    if api_key == "":
        raise OpenAIError("The `api_key` argument must not be empty.")
    if api_key is not None and token_provider is not None:
        raise OpenAIError(
            "Bedrock authentication is ambiguous. Configure exactly one explicit mode: bearer credential, "
            "static AWS credentials, profile, or credential provider."
        )

    explicit_aws_auth = _has_explicit_aws_auth(
        aws_profile=aws_profile,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        aws_credentials_provider=aws_credentials_provider,
    )
    if (api_key is not None or token_provider is not None) and explicit_aws_auth:
        raise OpenAIError(
            "Bedrock authentication is ambiguous. Configure exactly one explicit mode: bearer credential, "
            "static AWS credentials, profile, or credential provider."
        )

    environment_token = os.environ.get("AWS_BEARER_TOKEN_BEDROCK")
    uses_environment_bearer = (
        api_key is None and token_provider is None and not explicit_aws_auth and bool(environment_token)
    )
    resolved_region = _configured_region(aws_region)
    uses_region_derived_base_url = _uses_region_derived_base_url(base_url)

    provider_base_url: str | httpx.URL | None | NotGiven
    if isinstance(base_url, str) and not base_url.strip():
        provider_base_url = None
    elif base_url is None:
        provider_base_url = NOT_GIVEN
    else:
        provider_base_url = base_url

    provider = bedrock(
        region=aws_region,
        base_url=provider_base_url,
        api_key=api_key if api_key is not None else environment_token if uses_environment_bearer else NOT_GIVEN,
        token_provider=token_provider,
        access_key_id=aws_access_key_id,
        secret_access_key=aws_secret_access_key,
        session_token=aws_session_token,
        profile=aws_profile,
        credential_provider=aws_credentials_provider,
    )
    state = _LegacyBedrockState(
        explicit_api_key=api_key,
        token_provider=token_provider,
        aws_region=resolved_region,
        region_was_explicit=(
            bool(aws_region and aws_region.strip()) if region_was_explicit is None else region_was_explicit
        ),
        aws_profile=aws_profile,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        aws_credentials_provider=aws_credentials_provider,
        uses_environment_bearer=uses_environment_bearer,
        environment_bearer_token=environment_token if uses_environment_bearer else None,
        uses_region_derived_base_url=uses_region_derived_base_url,
    )
    return provider, state, api_key or (environment_token if uses_environment_bearer else "") or ""


def _copy_configuration(
    client: BedrockOpenAI | AsyncBedrockOpenAI,
    *,
    api_key: str | None,
    token_provider: BedrockTokenProvider | AsyncBedrockTokenProvider | None,
    aws_region: str | None,
    aws_profile: str | None,
    aws_access_key_id: str | None,
    aws_secret_access_key: str | None,
    aws_session_token: str | None,
    aws_credentials_provider: AwsCredentialsProvider | None,
    base_url: str | httpx.URL | None,
) -> tuple[dict[str, object], _Provider | None, _LegacyBedrockState | None]:
    _synchronize_legacy_routing_state(client)
    state = client._bedrock_state
    current_api_key = client.api_key or ""
    api_key_was_mutated = state.token_provider is None and current_api_key != _state_api_key(state)
    aws_override = _has_explicit_aws_auth(
        aws_profile=aws_profile,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        aws_credentials_provider=aws_credentials_provider,
    )
    explicit_bearer_override = api_key is not None or token_provider is not None
    if explicit_bearer_override and aws_override:
        raise OpenAIError(
            "Bedrock authentication is ambiguous. Configure exactly one explicit mode: bearer credential, "
            "static AWS credentials, profile, or credential provider."
        )

    effective_api_key = (
        api_key
        if api_key is not None
        else current_api_key
        if api_key_was_mutated and token_provider is None and not aws_override
        else None
    )
    bearer_override = effective_api_key is not None or token_provider is not None

    routing_override = aws_region is not None or base_url is not None
    if not bearer_override and not aws_override and not routing_override:
        _refresh_legacy_provider_runtime(client)
        return {}, client._bedrock_provider, client._bedrock_state

    if bearer_override:
        next_api_key = effective_api_key
        next_token_provider = token_provider
        next_profile = None
        next_access_key_id = None
        next_secret_access_key = None
        next_session_token = None
        next_credentials_provider = None
    elif aws_override:
        next_api_key = None
        next_token_provider = None
        next_profile = aws_profile
        next_access_key_id = aws_access_key_id
        next_secret_access_key = aws_secret_access_key
        next_session_token = aws_session_token
        next_credentials_provider = aws_credentials_provider
    else:
        next_api_key = state.explicit_api_key
        next_token_provider = state.token_provider
        if state.uses_environment_bearer:
            next_api_key = state.environment_bearer_token or _environment_bearer_token()
            next_token_provider = None
        next_profile = state.aws_profile
        next_access_key_id = state.aws_access_key_id
        next_secret_access_key = state.aws_secret_access_key
        next_session_token = state.aws_session_token
        next_credentials_provider = state.aws_credentials_provider

    next_region = aws_region if aws_region is not None else client.aws_region
    next_region_was_explicit = aws_region is not None or state.region_was_explicit
    if aws_profile is not None and aws_region is None and not state.region_was_explicit:
        next_region = None

    if base_url is not None:
        next_base_url: str | httpx.URL | None = base_url
    elif state.uses_region_derived_base_url:
        next_base_url = ""
    else:
        next_base_url = client.base_url

    provider_kwargs: dict[str, object] = {
        "api_key": next_api_key,
        "bedrock_token_provider": next_token_provider,
        "aws_region": next_region,
        "aws_profile": next_profile,
        "aws_access_key_id": next_access_key_id,
        "aws_secret_access_key": next_secret_access_key,
        "aws_session_token": next_session_token,
        "aws_credentials_provider": next_credentials_provider,
        "base_url": next_base_url,
    }
    if _constructor_accepts_keyword(client.__class__.__init__, "_region_was_explicit"):
        provider_kwargs["_region_was_explicit"] = next_region_was_explicit

    return provider_kwargs, None, None


def _legacy_runtime_signature(
    client: BedrockOpenAI | AsyncBedrockOpenAI,
    configuration: _LegacyAuthConfiguration,
) -> _LegacyRuntimeSignature:
    mode, credential = configuration
    # This is an opaque, process-local change detector, not a password hash.
    credential_identity: object = (
        hmac.digest(credential.encode(), _LEGACY_SIGNATURE_NONCE, "sha256")
        if isinstance(credential, str)
        else id(credential)
    )
    return _LegacyRuntimeSignature(
        mode=mode,
        base_url=str(client.base_url),
        region=client.aws_region,
        credential_identity=credential_identity,
    )


def _provider_for_legacy_client(
    client: BedrockOpenAI | AsyncBedrockOpenAI,
    configuration: _LegacyAuthConfiguration,
) -> _Provider:
    mode, credential = configuration
    if mode == "bearer":
        if not isinstance(credential, str) or not credential:
            raise OpenAIError("The Bedrock bearer credential must not be empty.")
        return bedrock(
            region=client.aws_region,
            base_url=client.base_url,
            api_key=credential,
        )
    if mode == "token_provider":
        return bedrock(
            region=client.aws_region,
            base_url=client.base_url,
            token_provider=cast("AsyncBedrockTokenProvider", credential),
        )

    state = client._bedrock_state
    return bedrock(
        region=client.aws_region,
        base_url=client.base_url,
        profile=state.aws_profile,
        access_key_id=state.aws_access_key_id,
        secret_access_key=state.aws_secret_access_key,
        session_token=state.aws_session_token,
        credential_provider=state.aws_credentials_provider,
    )


def _synchronize_legacy_routing_state(client: BedrockOpenAI | AsyncBedrockOpenAI) -> None:
    previous_signature = client._bedrock_runtime_signature
    base_url_changed = str(client.base_url) != previous_signature.base_url
    region_changed = client.aws_region != previous_signature.region
    if base_url_changed:
        client._bedrock_state = replace(client._bedrock_state, uses_region_derived_base_url=False)
        client._uses_region_derived_base_url = False
    if region_changed:
        client._bedrock_state = replace(
            client._bedrock_state,
            aws_region=client.aws_region,
            region_was_explicit=client.aws_region is not None,
        )
        if client._bedrock_state.uses_region_derived_base_url and client.aws_region is not None:
            client.base_url = f"https://bedrock-mantle.{client.aws_region}.api.aws/openai/v1"


def _refresh_legacy_provider_runtime(client: BedrockOpenAI | AsyncBedrockOpenAI) -> None:
    _synchronize_legacy_routing_state(client)
    configuration = client._legacy_auth_configuration()
    signature = _legacy_runtime_signature(client, configuration)
    if signature == client._bedrock_runtime_signature:
        return

    provider = _provider_for_legacy_client(client, configuration)
    client._bedrock_provider = provider
    client._provider = provider
    client._provider_runtime = _configure_provider(provider)
    if (
        isinstance(client._provider_runtime, _BedrockProviderRuntime)
        and client.aws_region is None
        and client._provider_runtime.region is not None
    ):
        client.aws_region = client._provider_runtime.region
        client._bedrock_state = replace(client._bedrock_state, aws_region=client.aws_region)
    client._bedrock_runtime_signature = _legacy_runtime_signature(client, configuration)


class BedrockOpenAI(OpenAI):
    """Compatibility client for Amazon Bedrock's OpenAI-compatible endpoint."""

    _bedrock_provider: _Provider
    _bedrock_state: _LegacyBedrockState
    _bedrock_token_provider: BedrockTokenProvider | None
    _uses_region_derived_base_url: bool
    _bedrock_runtime_signature: _LegacyRuntimeSignature
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
        _provider: _Provider | None = None,
        _state: _LegacyBedrockState | None = None,
        _region_was_explicit: bool | None = None,
    ) -> None:
        if _provider is None or _state is None:
            _provider, _state, public_api_key = _legacy_provider(
                api_key=api_key,
                token_provider=bedrock_token_provider,
                aws_region=aws_region,
                aws_profile=aws_profile,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
                aws_credentials_provider=aws_credentials_provider,
                base_url=base_url,
                region_was_explicit=_region_was_explicit,
            )
        else:
            public_api_key = (
                _state.explicit_api_key
                or (_state.environment_bearer_token if _state.uses_environment_bearer else "")
                or ""
            )

        super().__init__(
            provider=_provider,
            organization=organization,
            project=project,
            webhook_secret=webhook_secret,
            websocket_base_url=websocket_base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
            _enforce_credentials=False,
        )

        self._bedrock_provider = _provider
        self._bedrock_state = _state
        self._bedrock_token_provider = cast("BedrockTokenProvider | None", _state.token_provider)
        self._uses_region_derived_base_url = _state.uses_region_derived_base_url
        canonical_region = re.fullmatch(r"bedrock-mantle\.([a-z0-9-]+)\.api\.aws", self.base_url.host)
        provider_region = (
            self._provider_runtime.region if isinstance(self._provider_runtime, _BedrockProviderRuntime) else None
        )
        self.aws_region = (
            _state.aws_region
            or provider_region
            or (canonical_region.group(1) if canonical_region is not None else None)
        )
        self._bedrock_state = replace(_state, aws_region=self.aws_region)
        self.api_key = public_api_key or ""
        self._bedrock_runtime_signature = _legacy_runtime_signature(self, self._legacy_auth_configuration())

    def _legacy_auth_configuration(self) -> _LegacyAuthConfiguration:
        if self._bedrock_token_provider is not None:
            return ("token_provider", self._bedrock_token_provider)
        if (
            self._bedrock_state.explicit_api_key is not None
            or self._bedrock_state.uses_environment_bearer
            or self.api_key
        ):
            return ("bearer", self.api_key)
        return ("aws", None)

    def _uses_aws_auth(self) -> bool:
        return (
            self._bedrock_state.explicit_api_key is None
            and not self.api_key
            and self._bedrock_token_provider is None
            and not self._bedrock_state.uses_environment_bearer
        )

    @override
    def _refresh_api_key(self) -> str:
        if self._bedrock_state.uses_environment_bearer:
            captured = self._bedrock_state.environment_bearer_token or ""
            return self.api_key if self.api_key and self.api_key != captured else captured
        if self._bedrock_token_provider is not None:
            token = cast(object, self._bedrock_token_provider())
            if not isinstance(token, str) or not token:
                raise ValueError("Expected `bedrock_token_provider` argument to return a non-empty string.")
            return token
        return self.api_key

    @override
    def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
        _refresh_legacy_provider_runtime(self)
        return super()._prepare_options(options)

    @override
    def copy(
        self,
        *,
        api_key: str | BedrockTokenProvider | None = None,
        admin_api_key: str | None = None,
        workload_identity: WorkloadIdentity | None = None,
        provider: _Provider | None | NotGiven = NOT_GIVEN,
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
        if callable(api_key):
            raise OpenAIError("Pass refreshable Bedrock credentials via `bedrock_token_provider`, not `api_key`.")
        if not isinstance(provider, NotGiven):
            raise OpenAIError("Configure `provider` on `OpenAI`, not on `BedrockOpenAI.with_options()`.")
        if admin_api_key is not None or workload_identity is not None:
            raise OpenAIError("BedrockOpenAI only supports Bedrock bearer token or AWS credential authentication.")
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")
        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

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

        provider_kwargs, inherited_provider, inherited_state = _copy_configuration(
            self,
            api_key=api_key,
            token_provider=bedrock_token_provider,
            aws_region=aws_region,
            aws_profile=aws_profile,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            aws_credentials_provider=aws_credentials_provider,
            base_url=base_url,
        )
        constructor_kwargs: dict[str, Any] = {
            **provider_kwargs,
            "organization": organization if organization is not None else self.organization,
            "project": project if project is not None else self.project,
            "webhook_secret": webhook_secret if webhook_secret is not None else self.webhook_secret,
            "websocket_base_url": websocket_base_url if websocket_base_url is not None else self.websocket_base_url,
            "timeout": self.timeout if isinstance(timeout, NotGiven) else timeout,
            "http_client": http_client or self._client,
            "max_retries": max_retries if is_given(max_retries) else self.max_retries,
            "default_headers": headers,
            "default_query": params,
            "_enforce_credentials": True if _enforce_credentials is None else _enforce_credentials,
            **_extra_kwargs,
        }
        if inherited_provider is not None and _constructor_accepts_keyword(self.__class__.__init__, "_provider"):
            constructor_kwargs["_provider"] = inherited_provider
            constructor_kwargs["_state"] = inherited_state
        elif inherited_provider is not None:
            constructor_kwargs.update(
                api_key=self._bedrock_state.explicit_api_key or self._bedrock_state.environment_bearer_token,
                bedrock_token_provider=self._bedrock_state.token_provider,
                aws_region=self._bedrock_state.aws_region,
                aws_profile=self._bedrock_state.aws_profile,
                aws_access_key_id=self._bedrock_state.aws_access_key_id,
                aws_secret_access_key=self._bedrock_state.aws_secret_access_key,
                aws_session_token=self._bedrock_state.aws_session_token,
                aws_credentials_provider=self._bedrock_state.aws_credentials_provider,
                base_url="" if self._bedrock_state.uses_region_derived_base_url else self.base_url,
            )
            constructor_kwargs = {
                name: value
                for name, value in constructor_kwargs.items()
                if _constructor_accepts_keyword(self.__class__.__init__, name)
            }
        elif self.__class__ is not BedrockOpenAI:
            constructor_kwargs = {
                name: value
                for name, value in constructor_kwargs.items()
                if value is not None or _constructor_accepts_keyword(self.__class__.__init__, name)
            }
        return self.__class__(**constructor_kwargs)

    with_options = copy


class AsyncBedrockOpenAI(AsyncOpenAI):
    """Async compatibility client for Amazon Bedrock's OpenAI-compatible endpoint."""

    _bedrock_provider: _Provider
    _bedrock_state: _LegacyBedrockState
    _bedrock_token_provider: AsyncBedrockTokenProvider | None
    _uses_region_derived_base_url: bool
    _bedrock_runtime_signature: _LegacyRuntimeSignature
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
        _provider: _Provider | None = None,
        _state: _LegacyBedrockState | None = None,
        _region_was_explicit: bool | None = None,
    ) -> None:
        if _provider is None or _state is None:
            _provider, _state, public_api_key = _legacy_provider(
                api_key=api_key,
                token_provider=bedrock_token_provider,
                aws_region=aws_region,
                aws_profile=aws_profile,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
                aws_credentials_provider=aws_credentials_provider,
                base_url=base_url,
                region_was_explicit=_region_was_explicit,
            )
        else:
            public_api_key = (
                _state.explicit_api_key
                or (_state.environment_bearer_token if _state.uses_environment_bearer else "")
                or ""
            )

        super().__init__(
            provider=_provider,
            organization=organization,
            project=project,
            webhook_secret=webhook_secret,
            websocket_base_url=websocket_base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
            _enforce_credentials=False,
        )

        self._bedrock_provider = _provider
        self._bedrock_state = _state
        self._bedrock_token_provider = cast("AsyncBedrockTokenProvider | None", _state.token_provider)
        self._uses_region_derived_base_url = _state.uses_region_derived_base_url
        canonical_region = re.fullmatch(r"bedrock-mantle\.([a-z0-9-]+)\.api\.aws", self.base_url.host)
        provider_region = (
            self._provider_runtime.region if isinstance(self._provider_runtime, _BedrockProviderRuntime) else None
        )
        self.aws_region = (
            _state.aws_region
            or provider_region
            or (canonical_region.group(1) if canonical_region is not None else None)
        )
        self._bedrock_state = replace(_state, aws_region=self.aws_region)
        self.api_key = public_api_key or ""
        self._bedrock_runtime_signature = _legacy_runtime_signature(self, self._legacy_auth_configuration())

    def _legacy_auth_configuration(self) -> _LegacyAuthConfiguration:
        if self._bedrock_token_provider is not None:
            return ("token_provider", self._bedrock_token_provider)
        if (
            self._bedrock_state.explicit_api_key is not None
            or self._bedrock_state.uses_environment_bearer
            or self.api_key
        ):
            return ("bearer", self.api_key)
        return ("aws", None)

    def _uses_aws_auth(self) -> bool:
        return (
            self._bedrock_state.explicit_api_key is None
            and not self.api_key
            and self._bedrock_token_provider is None
            and not self._bedrock_state.uses_environment_bearer
        )

    @override
    async def _refresh_api_key(self) -> str:
        if self._bedrock_state.uses_environment_bearer:
            captured = self._bedrock_state.environment_bearer_token or ""
            return self.api_key if self.api_key and self.api_key != captured else captured
        if self._bedrock_token_provider is not None:
            token = cast(object, self._bedrock_token_provider())
            if inspect.isawaitable(token):
                token = await token
            if not isinstance(token, str) or not token:
                raise ValueError("Expected `bedrock_token_provider` argument to return a non-empty string.")
            return token
        return self.api_key

    @override
    async def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
        _refresh_legacy_provider_runtime(self)
        return await super()._prepare_options(options)

    @override
    def copy(
        self,
        *,
        api_key: str | AsyncBedrockTokenProvider | None = None,
        admin_api_key: str | None = None,
        workload_identity: WorkloadIdentity | None = None,
        provider: _Provider | None | NotGiven = NOT_GIVEN,
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
        if callable(api_key):
            raise OpenAIError("Pass refreshable Bedrock credentials via `bedrock_token_provider`, not `api_key`.")
        if not isinstance(provider, NotGiven):
            raise OpenAIError("Configure `provider` on `AsyncOpenAI`, not on `AsyncBedrockOpenAI.with_options()`.")
        if admin_api_key is not None or workload_identity is not None:
            raise OpenAIError("AsyncBedrockOpenAI only supports Bedrock bearer token or AWS credential authentication.")
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")
        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

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

        provider_kwargs, inherited_provider, inherited_state = _copy_configuration(
            self,
            api_key=api_key,
            token_provider=bedrock_token_provider,
            aws_region=aws_region,
            aws_profile=aws_profile,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            aws_credentials_provider=aws_credentials_provider,
            base_url=base_url,
        )
        constructor_kwargs: dict[str, Any] = {
            **provider_kwargs,
            "organization": organization if organization is not None else self.organization,
            "project": project if project is not None else self.project,
            "webhook_secret": webhook_secret if webhook_secret is not None else self.webhook_secret,
            "websocket_base_url": websocket_base_url if websocket_base_url is not None else self.websocket_base_url,
            "timeout": self.timeout if isinstance(timeout, NotGiven) else timeout,
            "http_client": http_client or self._client,
            "max_retries": max_retries if is_given(max_retries) else self.max_retries,
            "default_headers": headers,
            "default_query": params,
            "_enforce_credentials": True if _enforce_credentials is None else _enforce_credentials,
            **_extra_kwargs,
        }
        if inherited_provider is not None and _constructor_accepts_keyword(self.__class__.__init__, "_provider"):
            constructor_kwargs["_provider"] = inherited_provider
            constructor_kwargs["_state"] = inherited_state
        elif inherited_provider is not None:
            constructor_kwargs.update(
                api_key=self._bedrock_state.explicit_api_key or self._bedrock_state.environment_bearer_token,
                bedrock_token_provider=self._bedrock_state.token_provider,
                aws_region=self._bedrock_state.aws_region,
                aws_profile=self._bedrock_state.aws_profile,
                aws_access_key_id=self._bedrock_state.aws_access_key_id,
                aws_secret_access_key=self._bedrock_state.aws_secret_access_key,
                aws_session_token=self._bedrock_state.aws_session_token,
                aws_credentials_provider=self._bedrock_state.aws_credentials_provider,
                base_url="" if self._bedrock_state.uses_region_derived_base_url else self.base_url,
            )
            constructor_kwargs = {
                name: value
                for name, value in constructor_kwargs.items()
                if _constructor_accepts_keyword(self.__class__.__init__, name)
            }
        elif self.__class__ is not AsyncBedrockOpenAI:
            constructor_kwargs = {
                name: value
                for name, value in constructor_kwargs.items()
                if value is not None or _constructor_accepts_keyword(self.__class__.__init__, name)
            }
        return self.__class__(**constructor_kwargs)

    with_options = copy


__all__ = [
    "BedrockOpenAI",
    "AsyncBedrockOpenAI",
    "BedrockTokenProvider",
    "AsyncBedrockTokenProvider",
    "AwsCredentialsProvider",
]
