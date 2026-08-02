from __future__ import annotations

import sys
import json
import threading
from typing import Any, Iterator, cast
from pathlib import Path
from datetime import datetime, timezone, timedelta
from contextlib import contextmanager
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing_extensions import override

import httpx
import pytest

from openai import OpenAI
from openai.providers import bedrock

_FUTURE_EXPIRATION = "2099-01-01T00:00:00Z"
_AWS_ENVIRONMENT_NAMES = (
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "AWS_SECURITY_TOKEN",
    "AWS_PROFILE",
    "AWS_DEFAULT_PROFILE",
    "AWS_REGION",
    "AWS_DEFAULT_REGION",
    "AWS_CONFIG_FILE",
    "AWS_SHARED_CREDENTIALS_FILE",
    "AWS_CREDENTIAL_FILE",
    "AWS_WEB_IDENTITY_TOKEN_FILE",
    "AWS_ROLE_ARN",
    "AWS_ROLE_SESSION_NAME",
    "AWS_CONTAINER_CREDENTIALS_FULL_URI",
    "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI",
    "AWS_CONTAINER_AUTHORIZATION_TOKEN",
    "AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE",
    "AWS_EC2_METADATA_DISABLED",
    "AWS_EC2_METADATA_SERVICE_ENDPOINT",
    "AWS_EC2_METADATA_SERVICE_ENDPOINT_MODE",
    "AWS_BEARER_TOKEN_BEDROCK",
    "AWS_BEDROCK_BASE_URL",
    "BOTO_CONFIG",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
    "NO_PROXY",
    "no_proxy",
)


def _isolate_aws_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> tuple[Path, Path]:
    for name in _AWS_ENVIRONMENT_NAMES:
        monkeypatch.delenv(name, raising=False)

    config_path = tmp_path / "config"
    credentials_path = tmp_path / "credentials"
    config_path.write_text("")
    credentials_path.write_text("")
    monkeypatch.setenv("AWS_CONFIG_FILE", str(config_path))
    monkeypatch.setenv("AWS_SHARED_CREDENTIALS_FILE", str(credentials_path))
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")
    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost")
    monkeypatch.setenv("no_proxy", "127.0.0.1,localhost")
    return config_path, credentials_path


def _signed_request(**provider_options: Any) -> httpx.Request:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, request=request, json={})

    with OpenAI(
        provider=bedrock(**provider_options),
        http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
    ) as client:
        client.get("/models", cast_to=httpx.Response)

    assert len(requests) == 1
    return requests[0]


def _credentials_metadata(name: str, *, expiration: str = _FUTURE_EXPIRATION) -> dict[str, str]:
    return {
        "access_key": f"{name}-access-key",
        "secret_key": f"{name}-secret-key",
        "token": f"{name}-session-token",
        "expiry_time": expiration,
    }


def _assert_signed_with(request: httpx.Request, name: str, *, region: str) -> None:
    assert request.url.host == f"bedrock-mantle.{region}.api.aws"
    assert f"Credential={name}-access-key/" in request.headers["Authorization"]
    assert request.headers["X-Amz-Security-Token"] == f"{name}-session-token"


@contextmanager
def _metadata_server() -> Iterator[tuple[str, list[tuple[str, str, str | None]]]]:
    calls: list[tuple[str, str, str | None]] = []

    class Handler(BaseHTTPRequestHandler):
        def _respond(self, body: str, *, content_type: str = "text/plain") -> None:
            encoded = body.encode()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def do_PUT(self) -> None:
            calls.append(("PUT", self.path, self.headers.get("Authorization")))
            if self.path != "/latest/api/token":
                self.send_error(404)
                return
            self._respond("metadata-token")

        def do_GET(self) -> None:
            calls.append(("GET", self.path, self.headers.get("Authorization")))
            if self.path == "/container-credentials":
                self._respond(
                    json.dumps(
                        {
                            "AccessKeyId": "container-access-key",
                            "SecretAccessKey": "container-secret-key",
                            "Token": "container-session-token",
                            "Expiration": _FUTURE_EXPIRATION,
                        }
                    ),
                    content_type="application/json",
                )
                return
            if self.path == "/latest/meta-data/iam/security-credentials/":
                self._respond("instance-role")
                return
            if self.path == "/latest/meta-data/iam/security-credentials/instance-role":
                self._respond(
                    json.dumps(
                        {
                            "Code": "Success",
                            "LastUpdated": "2026-01-01T00:00:00Z",
                            "Type": "AWS-HMAC",
                            "AccessKeyId": "imds-access-key",
                            "SecretAccessKey": "imds-secret-key",
                            "Token": "imds-session-token",
                            "Expiration": _FUTURE_EXPIRATION,
                        }
                    ),
                    content_type="application/json",
                )
                return
            self.send_error(404)

        @override
        def log_message(self, format: str, *args: Any) -> None:
            del format, args
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = cast("tuple[str, int]", server.server_address)
    try:
        yield f"http://{host}:{port}", calls
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_default_chain_uses_environment_session_credentials(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _isolate_aws_environment(monkeypatch, tmp_path)
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "environment-access-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "environment-secret-key")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "environment-session-token")
    monkeypatch.setenv("AWS_REGION", "us-east-1")

    request = _signed_request()

    _assert_signed_with(request, "environment", region="us-east-1")


def test_default_chain_uses_aws_profile_and_shared_files(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config_path, credentials_path = _isolate_aws_environment(monkeypatch, tmp_path)
    credentials_path.write_text(
        "[work]\n"
        "aws_access_key_id = profile-access-key\n"
        "aws_secret_access_key = profile-secret-key\n"
        "aws_session_token = profile-session-token\n"
    )
    config_path.write_text("[profile work]\nregion = us-west-2\n")
    monkeypatch.setenv("AWS_PROFILE", "work")

    request = _signed_request()

    _assert_signed_with(request, "profile", region="us-west-2")


def test_default_chain_uses_assume_role_profile(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config_path, credentials_path = _isolate_aws_environment(monkeypatch, tmp_path)
    credentials_path.write_text(
        "[source]\naws_access_key_id = source-access-key\naws_secret_access_key = source-secret-key\n"
    )
    config_path.write_text(
        "[profile assumed]\n"
        "role_arn = arn:aws:iam::123456789012:role/example\n"
        "source_profile = source\n"
        "region = us-east-2\n"
    )
    monkeypatch.setenv("AWS_PROFILE", "assumed")
    credentials_module = pytest.importorskip("botocore.credentials")
    fetches = 0

    def fetch_credentials(_: object) -> dict[str, str]:
        nonlocal fetches
        fetches += 1
        return _credentials_metadata("assume-role")

    monkeypatch.setattr(credentials_module.AssumeRoleCredentialFetcher, "fetch_credentials", fetch_credentials)

    request = _signed_request()

    assert fetches == 1
    _assert_signed_with(request, "assume-role", region="us-east-2")


def test_default_chain_uses_sso_profile(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config_path, _ = _isolate_aws_environment(monkeypatch, tmp_path)
    config_path.write_text(
        "[profile sso]\n"
        "sso_session = company\n"
        "sso_account_id = 123456789012\n"
        "sso_role_name = Example\n"
        "region = us-west-1\n\n"
        "[sso-session company]\n"
        "sso_start_url = https://example.awsapps.com/start\n"
        "sso_region = us-east-1\n"
    )
    monkeypatch.setenv("AWS_PROFILE", "sso")
    credentials_module = pytest.importorskip("botocore.credentials")
    fetches = 0

    def fetch_credentials(_: object) -> dict[str, str]:
        nonlocal fetches
        fetches += 1
        return _credentials_metadata("sso")

    monkeypatch.setattr(credentials_module.SSOCredentialFetcher, "fetch_credentials", fetch_credentials)

    request = _signed_request()

    assert fetches == 1
    _assert_signed_with(request, "sso", region="us-west-1")


def test_default_chain_uses_web_identity(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _isolate_aws_environment(monkeypatch, tmp_path)
    token_path = tmp_path / "web-identity-token"
    token_path.write_text("web-identity-token")
    monkeypatch.setenv("AWS_ROLE_ARN", "arn:aws:iam::123456789012:role/web-identity")
    monkeypatch.setenv("AWS_ROLE_SESSION_NAME", "bedrock-test")
    monkeypatch.setenv("AWS_WEB_IDENTITY_TOKEN_FILE", str(token_path))
    monkeypatch.setenv("AWS_REGION", "eu-west-1")
    credentials_module = pytest.importorskip("botocore.credentials")
    fetches = 0

    def fetch_credentials(_: object) -> dict[str, str]:
        nonlocal fetches
        fetches += 1
        return _credentials_metadata("web-identity")

    monkeypatch.setattr(
        credentials_module.AssumeRoleWithWebIdentityCredentialFetcher,
        "fetch_credentials",
        fetch_credentials,
    )

    request = _signed_request()

    assert fetches == 1
    _assert_signed_with(request, "web-identity", region="eu-west-1")


def test_default_chain_uses_credential_process(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config_path, _ = _isolate_aws_environment(monkeypatch, tmp_path)
    process_path = tmp_path / "credentials_process.py"
    process_output = {
        "Version": 1,
        "AccessKeyId": "process-access-key",
        "SecretAccessKey": "process-secret-key",
        "SessionToken": "process-session-token",
        "Expiration": _FUTURE_EXPIRATION,
    }
    process_path.write_text(f"print({json.dumps(process_output)!r})\n")
    command = f"{json.dumps(sys.executable)} {json.dumps(str(process_path))}"
    config_path.write_text(f"[profile process]\nregion = ap-southeast-2\ncredential_process = {command}\n")
    monkeypatch.setenv("AWS_PROFILE", "process")

    request = _signed_request()

    _assert_signed_with(request, "process", region="ap-southeast-2")


@pytest.mark.parametrize("use_token_file", [False, True], ids=["ecs", "eks-pod-identity"])
def test_default_chain_uses_container_credentials(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, use_token_file: bool
) -> None:
    _isolate_aws_environment(monkeypatch, tmp_path)
    monkeypatch.setenv("AWS_REGION", "us-west-2")
    with _metadata_server() as (base_url, metadata_calls):
        monkeypatch.setenv("AWS_CONTAINER_CREDENTIALS_FULL_URI", f"{base_url}/container-credentials")
        expected_authorization = None
        if use_token_file:
            token_path = tmp_path / "container-authorization-token"
            token_path.write_text("pod-identity-token")
            monkeypatch.setenv("AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE", str(token_path))
            expected_authorization = "pod-identity-token"

        request = _signed_request()

    assert metadata_calls == [("GET", "/container-credentials", expected_authorization)]
    _assert_signed_with(request, "container", region="us-west-2")


def test_default_chain_uses_ec2_instance_metadata(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _isolate_aws_environment(monkeypatch, tmp_path)
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "false")
    with _metadata_server() as (base_url, metadata_calls):
        monkeypatch.setenv("AWS_EC2_METADATA_SERVICE_ENDPOINT", base_url)

        request = _signed_request()

    assert [(method, path) for method, path, _ in metadata_calls] == [
        ("PUT", "/latest/api/token"),
        ("GET", "/latest/meta-data/iam/security-credentials/"),
        ("GET", "/latest/meta-data/iam/security-credentials/instance-role"),
    ]
    _assert_signed_with(request, "imds", region="us-east-1")


def test_default_chain_refreshes_credentials_before_retry(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _isolate_aws_environment(monkeypatch, tmp_path)
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    credentials_module = pytest.importorskip("botocore.credentials")
    session_module = pytest.importorskip("botocore.session")
    refreshes = 0

    def expires_soon() -> str:
        return (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()

    def refresh() -> dict[str, str]:
        nonlocal refreshes
        refreshes += 1
        return _credentials_metadata(f"refresh-{refreshes}", expiration=expires_soon())

    credentials = credentials_module.RefreshableCredentials.create_from_metadata(
        metadata=_credentials_metadata("initial", expiration=expires_soon()),
        refresh_using=refresh,
        method="assume-role",
    )

    def get_credentials(_: object) -> Any:
        return credentials

    monkeypatch.setattr(session_module.Session, "get_credentials", get_credentials)
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(500 if len(requests) == 1 else 200, request=request, json={})

    with OpenAI(
        provider=bedrock(),
        max_retries=1,
        http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
    ) as client:
        client.get("/models", cast_to=httpx.Response)

    assert refreshes == 2
    assert len(requests) == 2
    _assert_signed_with(requests[0], "refresh-1", region="us-east-1")
    _assert_signed_with(requests[1], "refresh-2", region="us-east-1")
