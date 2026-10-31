"""Offline beta Realtime provider preflight and explicit-header compatibility."""

from __future__ import annotations

import threading
from typing import Any

import httpx2
import pytest
from websockets.sync.server import serve

import openai
from openai.auth import WorkloadIdentity, x509_workload_identity
from openai.providers import bedrock


@pytest.fixture(autouse=True)
def synthetic_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "OPENAI_API_KEY",
        "OPENAI_ADMIN_KEY",
        "OPENAI_BASE_URL",
        "OPENAI_ORG_ID",
        "OPENAI_PROJECT_ID",
        "OPENAI_CUSTOM_HEADERS",
        "OPENAI_WEBHOOK_SECRET",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")


def identity(kind: str, callbacks: list[str]) -> dict[str, Any]:
    def token() -> str:
        callbacks.append("token")
        raise AssertionError("implicit provider credential callback must not run")

    if kind == "bedrock":
        return {"provider": bedrock(region="us-east-1", token_provider=token)}
    if kind == "workload":
        return {
            "workload_identity": WorkloadIdentity(
                identity_provider_id="idp_synthetic",
                service_account_id="sa_synthetic",
                provider={"token_type": "jwt", "get_token": token},
            )
        }
    return {
        "workload_identity": x509_workload_identity(
            identity_provider_id="idp_synthetic", service_account_id="sa_synthetic"
        )
    }


async def connect(
    mode: str, kind: str, defaults: dict[str, Any], extra: dict[str, Any]
) -> tuple[BaseException | None, list[str], list[list[str]]]:
    callbacks: list[str] = []
    upgrades: list[list[str]] = []

    def issuer(_request: httpx2.Request) -> httpx2.Response:
        callbacks.append("issuer")
        raise AssertionError("implicit HTTP exchange must not run")

    def peer(socket: Any) -> None:
        assert socket.request.path.startswith("/v1/realtime?")
        assert socket.request.headers["X-Beta-Client"] == "synthetic-default"
        assert socket.request.headers["X-Beta-Connection"] == "synthetic-extra"
        upgrades.append(socket.request.headers.get_all("Authorization"))
        socket.close(1000)

    auth = identity(kind, callbacks)
    defaults = {"X-Beta-Client": "synthetic-default", **defaults}
    extra = {"X-Beta-Connection": "synthetic-extra", **extra}
    refused: BaseException | None = None
    with serve(peer, "127.0.0.1", 0, close_timeout=1) as server:
        worker = threading.Thread(target=server.serve_forever)
        worker.start()
        try:
            url = f"ws://127.0.0.1:{server.socket.getsockname()[1]}/v1"
            if mode == "sync":
                with openai.OpenAI(
                    **auth,
                    default_headers=defaults,
                    websocket_base_url=url,
                    http_client=httpx2.Client(transport=httpx2.MockTransport(issuer), trust_env=False),
                    max_retries=0,
                ) as client:
                    try:
                        with client.beta.realtime.connect(model="gpt-realtime", extra_headers=extra):
                            pass
                    except openai.OpenAIError as failure:
                        refused = failure
            else:
                async with openai.AsyncOpenAI(
                    **auth,
                    default_headers=defaults,
                    websocket_base_url=url,
                    http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(issuer), trust_env=False),
                    max_retries=0,
                ) as client:
                    try:
                        async with client.beta.realtime.connect(model="gpt-realtime", extra_headers=extra):
                            pass
                    except openai.OpenAIError as failure:
                        refused = failure
        finally:
            server.shutdown()
            worker.join(3)
        assert not worker.is_alive()
    return refused, callbacks, upgrades


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("kind", ["workload", "x509", "bedrock"])
async def test_bare_beta_provider_is_rejected_before_credentials_or_upgrade(mode: str, kind: str) -> None:
    refused, callbacks, upgrades = await connect(mode, kind, {}, {})
    assert refused is not None and "not supported by WebSocket" in str(refused)
    assert callbacks == [] and upgrades == []


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_x509_explicit_header_does_not_enable_unsupported_websocket_profile(mode: str) -> None:
    refused, callbacks, upgrades = await connect(mode, "x509", {}, {"Authorization": "Bearer synthetic-manual"})
    assert refused is not None and "not supported by WebSocket" in str(refused)
    assert callbacks == [] and upgrades == []


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("kind", ["workload", "bedrock"])
@pytest.mark.parametrize("header_profile", ["default", "extra", "override", "omit"])
async def test_beta_explicit_authorization_policy_is_preserved(mode: str, kind: str, header_profile: str) -> None:
    defaults: dict[str, Any] = {}
    extra: dict[str, Any] = {}
    expected = ["Bearer synthetic-manual"]
    if header_profile == "default":
        defaults = {"authorization": "Bearer synthetic-manual"}
    elif header_profile == "extra":
        extra = {"authorization": "Bearer synthetic-manual"}
    elif header_profile == "override":
        defaults = {"Authorization": "Bearer synthetic-overridden"}
        extra = {"AUTHORIZATION": "Bearer synthetic-manual"}
    else:
        defaults = {"Authorization": "Bearer synthetic-overridden"}
        extra = {"authorization": openai.omit}
        expected = []
    refused, callbacks, upgrades = await connect(mode, kind, defaults, extra)
    assert refused is None and callbacks == []
    assert upgrades == [expected]
