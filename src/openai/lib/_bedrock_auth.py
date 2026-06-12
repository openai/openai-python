from __future__ import annotations

import os
import importlib
from typing import Literal, Mapping, Callable, Protocol, cast
from dataclasses import field, dataclass

from .._exceptions import OpenAIError

AwsCredentialsProvider = Callable[[], object]


class _BotocoreSession(Protocol):
    def get_credentials(self) -> object | None: ...


_AUTHORIZATION = "authorization"
_UNSIGNED_PAYLOAD = "UNSIGNED-PAYLOAD"
_AWS_SIGNING_HEADERS = (
    _AUTHORIZATION,
    "x-amz-content-sha256",
    "x-amz-date",
    "x-amz-security-token",
)


@dataclass(frozen=True)
class BedrockBearerAuthConfig:
    source: Literal["explicit", "provider", "environment"]
    region_source: Literal["explicit", "environment"] | None = None


@dataclass(frozen=True)
class BedrockAwsAuthConfig:
    region: str
    source: Literal["static", "profile", "provider", "default"]
    region_source: Literal["explicit", "environment", "profile"] = "explicit"
    profile: str | None = None
    access_key_id: str | None = field(default=None, repr=False)
    secret_access_key: str | None = field(default=None, repr=False)
    session_token: str | None = field(default=None, repr=False)
    credentials_provider: AwsCredentialsProvider | None = field(default=None, repr=False, compare=False)


class BedrockAwsAuth:
    def __init__(self, config: BedrockAwsAuthConfig, *, session: _BotocoreSession | None = None) -> None:
        try:
            auth_module = importlib.import_module("botocore.auth")
            session_module = importlib.import_module("botocore.session")
            awsrequest_module = importlib.import_module("botocore.awsrequest")
            credentials_module = importlib.import_module("botocore.credentials")
        except ImportError as exc:
            raise OpenAIError(
                "Bedrock AWS authentication requires optional AWS dependencies. "
                "Install them with `pip install openai[bedrock]` and try again."
            ) from exc

        if session is None:
            try:
                session = session_module.Session(profile=config.profile)
            except Exception as exc:
                raise OpenAIError(
                    "Failed to resolve AWS credentials for Bedrock. Verify your AWS profile, environment variables, "
                    "or runtime identity configuration and try again."
                ) from exc

        assert session is not None
        self.config = config
        self._session = session
        self._credentials_provider = config.credentials_provider
        self._explicit_credentials = (
            credentials_module.Credentials(config.access_key_id, config.secret_access_key, config.session_token)
            if config.access_key_id is not None and config.secret_access_key is not None
            else None
        )
        self._aws_request_cls = awsrequest_module.AWSRequest
        self._sigv4_auth_cls = auth_module.SigV4Auth

    @classmethod
    def resolve(
        cls,
        *,
        region: str | None,
        profile: str | None,
        access_key_id: str | None,
        secret_access_key: str | None,
        session_token: str | None,
        credentials_provider: AwsCredentialsProvider | None,
    ) -> BedrockAwsAuth:
        try:
            session_module = importlib.import_module("botocore.session")
        except ImportError as exc:
            raise OpenAIError(
                "Bedrock AWS authentication requires optional AWS dependencies. "
                "Install them with `pip install openai[bedrock]` and try again."
            ) from exc

        try:
            session = session_module.Session(profile=profile)
            resolved_region, region_source = resolve_aws_region_with_source(region, session=session)
        except OpenAIError:
            raise
        except Exception as exc:
            raise OpenAIError(
                "Failed to resolve AWS credentials for Bedrock. Verify your AWS profile, environment variables, "
                "or runtime identity configuration and try again."
            ) from exc

        source: Literal["static", "profile", "provider", "default"]
        if access_key_id is not None:
            source = "static"
        elif profile is not None:
            source = "profile"
        elif credentials_provider is not None:
            source = "provider"
        else:
            source = "default"

        config = BedrockAwsAuthConfig(
            region=resolved_region,
            source=source,
            region_source=region_source,
            profile=profile,
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            session_token=session_token,
            credentials_provider=credentials_provider,
        )
        return cls(config, session=session)

    def sign(self, *, method: str, url: str, headers: Mapping[str, str], body: bytes | None) -> dict[str, str]:
        try:
            credentials = (
                self._credentials_provider()
                if self._credentials_provider is not None
                else self._explicit_credentials or self._session.get_credentials()
            )
            if credentials is None:
                raise OpenAIError(
                    "Could not find credentials for Bedrock. Pass a bearer credential or AWS credentials, "
                    "set `AWS_BEARER_TOKEN_BEDROCK`, or configure the default AWS credential chain."
                )

            get_frozen_credentials = getattr(credentials, "get_frozen_credentials", None)
            if callable(get_frozen_credentials):
                credentials = get_frozen_credentials()

            signed_headers = {
                name: value for name, value in headers.items() if name.lower() not in _AWS_SIGNING_HEADERS
            }
            if body is None:
                signed_headers["X-Amz-Content-SHA256"] = _UNSIGNED_PAYLOAD

            aws_request = self._aws_request_cls(
                method=method,
                url=url,
                data=body,
                headers=signed_headers,
            )
            self._sigv4_auth_cls(credentials, "bedrock-mantle", self.config.region).add_auth(aws_request)
        except OpenAIError:
            raise
        except Exception as exc:
            raise OpenAIError(
                "Failed to resolve AWS credentials for Bedrock. Verify your AWS profile, environment variables, "
                "or runtime identity configuration and try again."
            ) from exc

        return dict(aws_request.headers.items())


def resolve_aws_region_with_source(
    aws_region: str | None, *, session: object | None = None
) -> tuple[str, Literal["explicit", "environment", "profile"]]:
    region = aws_region
    source: Literal["explicit", "environment", "profile"] = "explicit"
    if region is None or not region.strip():
        region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
        source = "environment"
    if (region is None or not region.strip()) and session is not None:
        get_config_variable = getattr(session, "get_config_variable", None)
        if callable(get_config_variable):
            region = cast("str | None", get_config_variable("region"))
            source = "profile"

    if region is None or not region.strip():
        raise OpenAIError(
            "Bedrock requires an AWS region. Pass `aws_region`, or set `AWS_REGION` or `AWS_DEFAULT_REGION`."
        )

    return region.strip(), source


def resolve_aws_region(aws_region: str | None, *, session: object | None = None) -> str:
    return resolve_aws_region_with_source(aws_region, session=session)[0]


def resolve_bedrock_env_token() -> str | None:
    return os.environ.get("AWS_BEARER_TOKEN_BEDROCK") or None


def has_explicit_aws_auth(
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


def validate_explicit_aws_auth(
    *,
    aws_profile: str | None,
    aws_access_key_id: str | None,
    aws_secret_access_key: str | None,
    aws_session_token: str | None,
    aws_credentials_provider: AwsCredentialsProvider | None,
) -> None:
    if (aws_access_key_id is None) != (aws_secret_access_key is None):
        raise OpenAIError(
            "Static AWS credentials require both `aws_access_key_id` and `aws_secret_access_key`. "
            "An `aws_session_token` may only be used with both."
        )

    credential_sources = sum(
        (
            aws_profile is not None,
            aws_access_key_id is not None,
            aws_credentials_provider is not None,
        )
    )
    if credential_sources > 1:
        raise OpenAIError(
            "Bedrock authentication is ambiguous. Configure exactly one explicit mode: bearer credential, "
            "static AWS credentials, profile, or credential provider."
        )

    if aws_session_token is not None and aws_access_key_id is None:
        raise OpenAIError(
            "Static AWS credentials require both `aws_access_key_id` and `aws_secret_access_key`. "
            "An `aws_session_token` may only be used with both."
        )
