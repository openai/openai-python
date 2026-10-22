"""Handwritten module-client provider selection and credential routing."""

from __future__ import annotations

import openai as _sdk

from .._client import OpenAI


def has_openai_credentials() -> bool:
    return _sdk._os.environ.get("OPENAI_API_KEY") is not None


def has_azure_credentials() -> bool:
    return _sdk.azure_endpoint is not None or _sdk._os.environ.get("AZURE_OPENAI_API_KEY") is not None


def has_azure_ad_credentials() -> bool:
    return (
        _sdk._os.environ.get("AZURE_OPENAI_AD_TOKEN") is not None
        or _sdk.azure_ad_token is not None
        or _sdk.azure_ad_token_provider is not None
    )


def load_client() -> OpenAI:
    if _sdk._client is None:
        if _sdk.azure_endpoint is None:
            _sdk.azure_endpoint = _sdk._os.environ.get("AZURE_OPENAI_ENDPOINT")
        if _sdk.api_version is None:
            _sdk.api_version = _sdk._os.environ.get("OPENAI_API_VERSION")
        if _sdk.api_type is None:
            has_openai = _sdk._has_openai_credentials()
            has_azure = _sdk._has_azure_credentials()
            has_azure_ad = _sdk._has_azure_ad_credentials()
            if has_openai and (has_azure or has_azure_ad):
                raise _sdk._AmbiguousModuleClientUsageError()
            if has_azure or has_azure_ad:
                _sdk.api_type = "azure"
            else:
                _sdk.api_type = "openai"
        if _sdk.api_type == "azure":
            _sdk._client = _sdk._AzureModuleClient(  # type: ignore
                api_version=_sdk.api_version,
                azure_endpoint=_sdk.azure_endpoint,
                api_key=_sdk.api_key,
                azure_ad_token=_sdk.azure_ad_token,
                azure_ad_token_provider=_sdk.azure_ad_token_provider,
                organization=_sdk.organization,
                base_url=_sdk.base_url,
                timeout=_sdk.timeout,
                max_retries=_sdk.max_retries,
                default_headers=_sdk.default_headers,
                default_query=_sdk.default_query,
                http_client=_sdk.http_client,
            )
            return _sdk._client
        if _sdk.api_type == "amazon-bedrock":
            _sdk._client = _sdk._BedrockModuleClient(
                api_key=_sdk.api_key,
                bedrock_token_provider=_sdk.bedrock_token_provider,
                organization=_sdk.organization,
                project=_sdk.project,
                webhook_secret=_sdk.webhook_secret,
                base_url=_sdk.base_url,
                timeout=_sdk.timeout,
                max_retries=_sdk.max_retries,
                default_headers=_sdk.default_headers,
                default_query=_sdk.default_query,
                http_client=_sdk.http_client,
            )
            return _sdk._client
        _sdk._client = _sdk._ModuleClient(
            api_key=_sdk.api_key,
            admin_api_key=_sdk.admin_api_key,
            organization=_sdk.organization,
            project=_sdk.project,
            webhook_secret=_sdk.webhook_secret,
            base_url=_sdk.base_url,
            timeout=_sdk.timeout,
            max_retries=_sdk.max_retries,
            default_headers=_sdk.default_headers,
            default_query=_sdk.default_query,
            http_client=_sdk.http_client,
            _enforce_credentials=False,
        )
        return _sdk._client
    return _sdk._client


def BedrockModuleClient_api_key(_self: _sdk._BedrockModuleClient) -> str | None:
    return _sdk.api_key if _sdk.api_key is not None else _sdk._bedrock_api_key


def BedrockModuleClient_api_key_setter(_self: _sdk._BedrockModuleClient, value: str | None) -> None:
    _sdk._bedrock_api_key = value


def BedrockModuleClient_refresh_api_key(
    _owner: type[_sdk._BedrockModuleClient], /, self: _sdk._BedrockModuleClient
) -> str:
    if _sdk.api_key is not None:
        return _sdk.api_key
    return super(_owner, self)._refresh_api_key()


def BedrockModuleClient_legacy_auth_configuration(
    _owner: type[_sdk._BedrockModuleClient], /, self: _sdk._BedrockModuleClient
) -> _sdk._bedrock._LegacyAuthConfiguration:
    if _sdk.api_key is not None:
        return ("bearer", _sdk.api_key)
    return super(_owner, self)._legacy_auth_configuration()


def AmbiguousModuleClientUsageError_init(
    _owner: type[_sdk._AmbiguousModuleClientUsageError], /, self: _sdk._AmbiguousModuleClientUsageError
) -> None:
    super(_owner, self).__init__(
        "Ambiguous use of module client; please set `openai.api_type` or the `OPENAI_API_TYPE` environment variable to `openai`, `azure`, or `amazon-bedrock`"
    )
