from __future__ import annotations

import threading
from typing import Any, Iterator, cast
from unittest.mock import Mock

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai._base_client import get_platform, platform_headers


@pytest.fixture(autouse=True)
def clear_platform_headers() -> Iterator[None]:
    # The SDK's lru_cache wrapper preserves the callable's original signature.
    cast(Any, platform_headers).cache_clear()
    yield
    cast(Any, platform_headers).cache_clear()


@pytest.mark.parametrize(
    "system,name,expected",
    [
        ("Darwin", "Darwin-iPhone12,1", "iOS"),
        ("Darwin", "Darwin-iPad7,11", "iOS"),
        ("Darwin", "macOS", "MacOS"),
        ("Windows", "Windows-11", "Windows"),
        ("Linux", "Linux-android12", "Android"),
        ("FreeBSD", "FreeBSD-14", "FreeBSD"),
        ("OpenBSD", "OpenBSD-7", "OpenBSD"),
        ("SunOS", "SunOS-5", "Other:sunos-5"),
        ("", "", "Unknown"),
    ],
)
def test_non_linux_platforms(monkeypatch: pytest.MonkeyPatch, system: str, name: str, expected: str) -> None:
    monkeypatch.setattr("openai._base_client.platform.system", lambda: system)
    monkeypatch.setattr("openai._base_client.platform.platform", lambda: name)
    os_release = Mock(side_effect=AssertionError("os-release must not be read"))
    monkeypatch.setattr("openai._base_client.platform.freedesktop_os_release", os_release)
    assert str(get_platform()) == expected
    os_release.assert_not_called()


@pytest.mark.parametrize(
    "release,expected",
    [({}, "Linux"), ({"ID": "ubuntu"}, "Linux"), ({"ID": "FREEBSD"}, "FreeBSD"), ({"ID": "openbsd"}, "OpenBSD")],
)
def test_linux_os_release(monkeypatch: pytest.MonkeyPatch, release: dict[str, str], expected: str) -> None:
    monkeypatch.setattr("openai._base_client.platform.system", lambda: "Linux")
    monkeypatch.setattr("openai._base_client.platform.platform", lambda: "Linux-6")
    monkeypatch.setattr("openai._base_client.platform.freedesktop_os_release", lambda: release)
    assert str(get_platform()) == expected


@pytest.mark.parametrize("error", [FileNotFoundError(), PermissionError(), OSError()])
def test_unreadable_os_release(monkeypatch: pytest.MonkeyPatch, error: OSError) -> None:
    monkeypatch.setattr("openai._base_client.platform.system", lambda: "Linux")
    monkeypatch.setattr("openai._base_client.platform.platform", lambda: "Linux-6")
    monkeypatch.setattr("openai._base_client.platform.freedesktop_os_release", Mock(side_effect=error))
    assert get_platform() == "Linux"


def test_platform_lookup_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("openai._base_client.platform.system", Mock(side_effect=OSError()))
    assert get_platform() == "Unknown"


def _linux_request_setup(monkeypatch: pytest.MonkeyPatch, expected: str) -> httpx2.MockTransport:
    monkeypatch.setattr("openai._base_client.platform.system", lambda: "Linux")
    monkeypatch.setattr("openai._base_client.platform.platform", lambda: "Linux-6")

    def handler(request: httpx2.Request) -> httpx2.Response:
        assert request.headers["X-Stainless-OS"] == expected
        return httpx2.Response(200, json={})

    return httpx2.MockTransport(handler)


def test_sync_request_platform_header(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = _linux_request_setup(monkeypatch, "Linux")
    monkeypatch.setattr("openai._base_client.platform.freedesktop_os_release", Mock(side_effect=FileNotFoundError()))
    with OpenAI(api_key="test-key", http_client=httpx2.Client(transport=transport, trust_env=False)) as client:
        assert client.get("/models", cast_to=httpx2.Response).status_code == 200


async def test_async_request_platform_header(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = _linux_request_setup(monkeypatch, "FreeBSD")
    event_loop_thread = threading.get_ident()
    calls: list[int] = []

    def os_release() -> dict[str, str]:
        calls.append(threading.get_ident())
        return {"ID": "freebsd"}

    monkeypatch.setattr("openai._base_client.platform.freedesktop_os_release", os_release)
    async with AsyncOpenAI(
        api_key="test-key", http_client=httpx2.AsyncClient(transport=transport, trust_env=False)
    ) as client:
        for _ in range(2):
            assert (await client.get("/models", cast_to=httpx2.Response)).status_code == 200
    assert len(calls) == 1
    assert calls[0] != event_loop_thread
