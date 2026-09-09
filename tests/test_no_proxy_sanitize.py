# Regression tests for NO_PROXY newline sanitization (issue #3303).
#
# httpx's ``get_environment_proxies()`` only splits on commas, so a trailing
# newline in ``NO_PROXY`` becomes part of the hostname and httpx raises
# ``InvalidURL``.  The SDK temporarily normalizes the env var during client
# construction and restores it afterwards, so unrelated clients are unaffected.

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest


@pytest.fixture(autouse=True)
def _restore_inherited_no_proxy(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:  # pyright: ignore[reportUnusedFunction]
    """Restore any NO_PROXY/no_proxy inherited from the test environment.

    The sanitizer mutates os.environ during client construction and restores
    it afterwards, but a test that fails mid-construction (or a test that
    deliberately leaves a value set) can leak into the next test.  Snapshot the
    inherited values up front and restore them after each test so the suite
    is deterministic regardless of the host environment.
    """
    inherited = {
        key: os.environ.get(key)
        for key in ("NO_PROXY", "no_proxy")
    }
    yield
    for key, val in inherited.items():
        if val is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, val)


def _set_no_proxy(monkeypatch: pytest.MonkeyPatch, value: str | None) -> None:
    """Set both NO_PROXY and no_proxy via monkeypatch for automatic cleanup."""
    if value is None:
        monkeypatch.delenv("NO_PROXY", raising=False)
        monkeypatch.delenv("no_proxy", raising=False)
    else:
        monkeypatch.setenv("NO_PROXY", value)
        monkeypatch.setenv("no_proxy", value)


def _mount_patterns(client: object) -> list[str]:
    return [k.pattern for k in client._mounts]  # type: ignore[attr-defined]


def test_sync_client_construction_with_newline_no_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    """A sync default client can be constructed when NO_PROXY has newlines."""
    from openai._base_client import _DefaultHttpxClient

    _set_no_proxy(monkeypatch, "localhost\n127.0.0.1")
    # Should not raise InvalidURL
    client = _DefaultHttpxClient()
    patterns = _mount_patterns(client)
    assert any("localhost" in p for p in patterns)
    assert any("127.0.0.1" in p for p in patterns)
    client.close()


def test_async_client_construction_with_newline_no_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    """An async default client can be constructed when NO_PROXY has newlines."""
    from openai._base_client import _DefaultAsyncHttpxClient

    _set_no_proxy(monkeypatch, "localhost\n127.0.0.1")
    # Should not raise InvalidURL
    client = _DefaultAsyncHttpxClient()
    patterns = _mount_patterns(client)
    assert any("localhost" in p for p in patterns)
    assert any("127.0.0.1" in p for p in patterns)


def test_env_restored_after_sync_client_construction(monkeypatch: pytest.MonkeyPatch) -> None:
    """os.environ is restored to its original value after client construction."""
    from openai._base_client import _DefaultHttpxClient

    original = "localhost\n127.0.0.1"
    _set_no_proxy(monkeypatch, original)
    client = _DefaultHttpxClient()
    client.close()
    import os

    assert os.environ.get("NO_PROXY") == original
    assert os.environ.get("no_proxy") == original


def test_env_restored_after_async_client_construction(monkeypatch: pytest.MonkeyPatch) -> None:
    """os.environ is restored after async client construction."""
    from openai._base_client import _DefaultAsyncHttpxClient

    original = "localhost\n127.0.0.1"
    _set_no_proxy(monkeypatch, original)
    _DefaultAsyncHttpxClient()
    import os

    assert os.environ.get("NO_PROXY") == original
    assert os.environ.get("no_proxy") == original


def test_trust_env_false_skips_sanitization(monkeypatch: pytest.MonkeyPatch) -> None:
    """When trust_env=False, NO_PROXY is not touched and no InvalidURL is raised."""
    from openai._base_client import _DefaultHttpxClient

    _set_no_proxy(monkeypatch, "localhost\n127.0.0.1")
    client = _DefaultHttpxClient(trust_env=False)
    import os

    # env should be untouched
    assert os.environ.get("NO_PROXY") == "localhost\n127.0.0.1"
    # no proxy mounts should be configured since trust_env=False
    assert client._mounts == {}
    client.close()


def test_trust_env_false_async_skips_sanitization(monkeypatch: pytest.MonkeyPatch) -> None:
    """Async client with trust_env=False skips NO_PROXY sanitization."""
    from openai._base_client import _DefaultAsyncHttpxClient

    _set_no_proxy(monkeypatch, "localhost\n127.0.0.1")
    client = _DefaultAsyncHttpxClient(trust_env=False)
    import os

    assert os.environ.get("NO_PROXY") == "localhost\n127.0.0.1"
    assert client._mounts == {}


def test_no_newline_no_mutation(monkeypatch: pytest.MonkeyPatch) -> None:
    """When NO_PROXY has no newlines, the env var is not modified at all."""
    from openai._base_client import _DefaultHttpxClient

    _set_no_proxy(monkeypatch, "localhost,127.0.0.1")
    client = _DefaultHttpxClient()
    client.close()
    import os

    assert os.environ.get("NO_PROXY") == "localhost,127.0.0.1"


def test_lowercase_no_proxy_sanitized(monkeypatch: pytest.MonkeyPatch) -> None:
    """Lowercase no_proxy is also sanitized."""
    from openai._base_client import _DefaultHttpxClient

    monkeypatch.delenv("NO_PROXY", raising=False)
    monkeypatch.setenv("no_proxy", "localhost\n127.0.0.1")
    client = _DefaultHttpxClient()
    client.close()
    import os

    # restored after construction
    assert os.environ.get("no_proxy") == "localhost\n127.0.0.1"


def test_multiple_newlines_sanitized(monkeypatch: pytest.MonkeyPatch) -> None:
    """Multiple newlines and whitespace are handled correctly."""
    from openai._base_client import _DefaultHttpxClient

    _set_no_proxy(monkeypatch, "localhost\n\n127.0.0.1\n.example.com\n")
    client = _DefaultHttpxClient()
    patterns = _mount_patterns(client)
    assert any("localhost" in p for p in patterns)
    assert any("127.0.0.1" in p for p in patterns)
    assert any("example.com" in p for p in patterns)
    client.close()
    import os

    # restored
    assert os.environ.get("NO_PROXY") == "localhost\n\n127.0.0.1\n.example.com\n"


def test_carriage_return_sanitized(monkeypatch: pytest.MonkeyPatch) -> None:
    """A lone \\r (from CRLF files where \\n was stripped) is also sanitized."""
    from openai._base_client import _DefaultHttpxClient

    _set_no_proxy(monkeypatch, "localhost\r127.0.0.1")
    client = _DefaultHttpxClient()
    patterns = _mount_patterns(client)
    assert any("localhost" in p for p in patterns)
    assert any("127.0.0.1" in p for p in patterns)
    client.close()
    import os

    assert os.environ.get("NO_PROXY") == "localhost\r127.0.0.1"


def test_crlf_sanitized(monkeypatch: pytest.MonkeyPatch) -> None:
    """CRLF (\\r\\n) line endings are sanitized correctly."""
    from openai._base_client import _DefaultHttpxClient

    _set_no_proxy(monkeypatch, "localhost\r\n127.0.0.1\r\n")
    client = _DefaultHttpxClient()
    patterns = _mount_patterns(client)
    assert any("localhost" in p for p in patterns)
    assert any("127.0.0.1" in p for p in patterns)
    client.close()


def test_aiohttp_client_construction_with_newline_no_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    """The aiohttp transport client also sanitizes NO_PROXY newlines."""
    pytest.importorskip("aiohttp")
    from openai._base_client import _DefaultAioHttpClient

    _set_no_proxy(monkeypatch, "localhost\n127.0.0.1")
    # Should not raise InvalidURL
    client = _DefaultAioHttpClient()
    patterns = _mount_patterns(client)
    assert any("localhost" in p for p in patterns)
    assert any("127.0.0.1" in p for p in patterns)


def test_aiohttp_client_trust_env_false_skips_sanitization(monkeypatch: pytest.MonkeyPatch) -> None:
    """The aiohttp transport client respects trust_env=False."""
    pytest.importorskip("aiohttp")
    from openai._base_client import _DefaultAioHttpClient

    _set_no_proxy(monkeypatch, "localhost\n127.0.0.1")
    _DefaultAioHttpClient(trust_env=False)
    import os

    assert os.environ.get("NO_PROXY") == "localhost\n127.0.0.1"


def test_concurrent_client_construction_serializes_sanitization(monkeypatch: pytest.MonkeyPatch) -> None:
    """Concurrent client constructions must not race on the env mutation.

    Without the lock, one call could restore the original (invalid) NO_PROXY
    value while another call's ``super().__init__()`` is still reading the
    environment, exposing the second client to InvalidURL.  The lock
    serializes the sanitize-construct-restore window so each call sees a
    consistent environment.
    """
    import threading

    from openai._base_client import _DefaultHttpxClient

    _set_no_proxy(monkeypatch, "localhost\n127.0.0.1")
    errors: list[Exception] = []

    def construct() -> None:
        try:
            _DefaultHttpxClient()
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=construct) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Concurrent constructions failed: {errors}"
    # The original (invalid) value must be restored after all constructions
    assert os.environ.get("NO_PROXY") == "localhost\n127.0.0.1"


def test_concurrent_no_proxy_update_not_clobbered(monkeypatch: pytest.MonkeyPatch) -> None:
    """An application update to NO_PROXY during construction is preserved.

    If application code changes NO_PROXY while a client is being constructed,
    the sanitizer must not clobber that update when it restores the original
    value — the update is newer and more relevant than the pre-construction
    value.
    """
    from openai._base_client import _sanitized_no_proxy

    _set_no_proxy(monkeypatch, "localhost\n127.0.0.1")

    with _sanitized_no_proxy():
        # Simulate application code updating NO_PROXY mid-construction.
        os.environ["NO_PROXY"] = "api.example.com"

    # The application's update must survive the sanitizer's restore.
    assert os.environ.get("NO_PROXY") == "api.example.com"


@pytest.mark.parametrize(
    "separator",
    ["\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029"],
)
def test_all_splitlines_separators_sanitized(monkeypatch: pytest.MonkeyPatch, separator: str) -> None:
    """Every line boundary recognized by str.splitlines() is sanitized.

    httpx rejects any non-printable character in the proxy hostname, so a
    NO_PROXY value containing a vertical tab, form feed, or Unicode line
    separator must be normalized just like a newline.
    """
    from openai._base_client import _DefaultHttpxClient

    _set_no_proxy(monkeypatch, f"localhost{separator}127.0.0.1")
    client = _DefaultHttpxClient()
    patterns = _mount_patterns(client)
    assert any("localhost" in p for p in patterns)
    assert any("127.0.0.1" in p for p in patterns)
    client.close()


def test_httpx2_factory_sanitizes_no_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    """The public DefaultHttpx2Client factory also sanitizes NO_PROXY."""
    from openai import DefaultHttpx2Client

    _set_no_proxy(monkeypatch, "localhost\n127.0.0.1")
    client = DefaultHttpx2Client()
    patterns = _mount_patterns(client)
    assert any("localhost" in p for p in patterns)
    assert any("127.0.0.1" in p for p in patterns)
    client.close()


def test_httpx2_factory_trust_env_false_skips_sanitization(monkeypatch: pytest.MonkeyPatch) -> None:
    """The public DefaultHttpx2Client factory respects trust_env=False."""
    from openai import DefaultHttpx2Client

    _set_no_proxy(monkeypatch, "localhost\n127.0.0.1")
    client = DefaultHttpx2Client(trust_env=False)
    assert os.environ.get("NO_PROXY") == "localhost\n127.0.0.1"
    assert client._mounts == {}
    client.close()


def test_async_httpx2_factory_sanitizes_no_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    """The public DefaultAsyncHttpx2Client factory also sanitizes NO_PROXY."""
    from openai import DefaultAsyncHttpx2Client

    _set_no_proxy(monkeypatch, "localhost\n127.0.0.1")
    client = DefaultAsyncHttpx2Client()
    patterns = _mount_patterns(client)
    assert any("localhost" in p for p in patterns)
    assert any("127.0.0.1" in p for p in patterns)


def test_sanitizer_lock_replaced_after_fork() -> None:
    """The sanitizer lock is replaced in the child after a fork.

    If a fork happens while another thread holds the lock, the child would
    inherit the acquired lock and block forever on the next client
    construction.  os.register_at_fork must replace it.
    """
    import multiprocessing

    import openai._base_client as base_client

    # Simulate the child state: acquire the lock in this process, then fork.
    base_client._no_proxy_sanitizer_lock.acquire()
    try:
        ctx = multiprocessing.get_context("fork")
        q = ctx.Queue()
        p = ctx.Process(
            target=lambda: q.put(base_client._no_proxy_sanitizer_lock.locked()),
        )
        p.start()
        p.join(timeout=10)
        child_locked = q.get(timeout=5)
    finally:
        base_client._no_proxy_sanitizer_lock.release()

    # The child must not inherit the acquired lock.
    assert child_locked is False
