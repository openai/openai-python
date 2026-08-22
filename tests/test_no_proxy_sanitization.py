"""Tests for NO_PROXY env var sanitization during httpx client init.

Regression tests for issue #3303: Docker/.env files can leave newline or
carriage return characters in NO_PROXY, which httpx's comma-only splitter
treats as part of the hostname, causing InvalidURL.
"""

from __future__ import annotations

import os
from typing import Iterator

import pytest

from openai._base_client import (
    _save_no_proxy_env,
    _DefaultHttpxClient,
    _restore_no_proxy_env,
    _sanitize_no_proxy_env,
    _DefaultAsyncHttpxClient,
)


@pytest.fixture(autouse=True)
def clean_no_proxy() -> Iterator[None]:
    """Remove NO_PROXY/no_proxy before and after each test."""
    for var in ("NO_PROXY", "no_proxy"):
        os.environ.pop(var, None)
    yield
    for var in ("NO_PROXY", "no_proxy"):
        os.environ.pop(var, None)


class TestSanitizeNoProxyEnv:
    def test_newlines_replaced_with_commas(self) -> None:
        os.environ["NO_PROXY"] = "localhost\n127.0.0.1\n.example.com"
        _sanitize_no_proxy_env(trust_env=True)
        assert os.environ["NO_PROXY"] == "localhost,127.0.0.1,.example.com"

    def test_carriage_returns_replaced(self) -> None:
        os.environ["NO_PROXY"] = "localhost\r127.0.0.1"
        _sanitize_no_proxy_env(trust_env=True)
        assert os.environ["NO_PROXY"] == "localhost,127.0.0.1"

    def test_crlf_handled(self) -> None:
        os.environ["NO_PROXY"] = "localhost\r\n127.0.0.1\r\n"
        _sanitize_no_proxy_env(trust_env=True)
        assert os.environ["NO_PROXY"] == "localhost,127.0.0.1"

    def test_trailing_newline_stripped(self) -> None:
        os.environ["NO_PROXY"] = "localhost,127.0.0.1\n"
        _sanitize_no_proxy_env(trust_env=True)
        assert os.environ["NO_PROXY"] == "localhost,127.0.0.1"

    def test_already_clean_value_unchanged(self) -> None:
        os.environ["NO_PROXY"] = "localhost,127.0.0.1"
        _sanitize_no_proxy_env(trust_env=True)
        assert os.environ["NO_PROXY"] == "localhost,127.0.0.1"

    def test_no_env_var_unchanged(self) -> None:
        _sanitize_no_proxy_env(trust_env=True)
        assert "NO_PROXY" not in os.environ
        assert "no_proxy" not in os.environ

    def test_lowercase_var_sanitized(self) -> None:
        os.environ["no_proxy"] = "localhost\n127.0.0.1"
        _sanitize_no_proxy_env(trust_env=True)
        assert os.environ["no_proxy"] == "localhost,127.0.0.1"

    def test_trust_env_false_skips_sanitization(self) -> None:
        os.environ["NO_PROXY"] = "localhost\n127.0.0.1"
        _sanitize_no_proxy_env(trust_env=False)
        # Should remain unchanged when trust_env=False
        assert os.environ["NO_PROXY"] == "localhost\n127.0.0.1"

    def test_empty_lines_skipped(self) -> None:
        os.environ["NO_PROXY"] = "localhost\n\n127.0.0.1\n"
        _sanitize_no_proxy_env(trust_env=True)
        assert os.environ["NO_PROXY"] == "localhost,127.0.0.1"

    def test_whitespace_stripped(self) -> None:
        os.environ["NO_PROXY"] = "  localhost  \n  127.0.0.1  "
        _sanitize_no_proxy_env(trust_env=True)
        assert os.environ["NO_PROXY"] == "localhost,127.0.0.1"


class TestSaveRestoreNoProxyEnv:
    def test_save_and_restore_unchanged(self) -> None:
        os.environ["NO_PROXY"] = "localhost,127.0.0.1"
        saved = _save_no_proxy_env()
        _sanitize_no_proxy_env(trust_env=True)
        _restore_no_proxy_env(saved)
        assert os.environ["NO_PROXY"] == "localhost,127.0.0.1"

    def test_save_and_restore_with_newlines(self) -> None:
        os.environ["NO_PROXY"] = "localhost\n127.0.0.1"
        saved = _save_no_proxy_env()
        _sanitize_no_proxy_env(trust_env=True)
        # After sanitization, the env is changed
        assert os.environ["NO_PROXY"] == "localhost,127.0.0.1"
        # After restore, the original value is back
        _restore_no_proxy_env(saved)
        assert os.environ["NO_PROXY"] == "localhost\n127.0.0.1"

    def test_save_and_restore_missing_var(self) -> None:
        saved = _save_no_proxy_env()
        os.environ["NO_PROXY"] = "should-be-removed"
        _restore_no_proxy_env(saved)
        assert "NO_PROXY" not in os.environ


class TestClientConstruction:
    def test_sync_client_restores_env_after_init(self) -> None:
        """The sync client should restore the original NO_PROXY value after init."""
        original = "localhost\n127.0.0.1"
        os.environ["NO_PROXY"] = original
        client = _DefaultHttpxClient()
        client.close()
        # The original (unsanitized) value should be restored
        assert os.environ["NO_PROXY"] == original

    def test_async_client_restores_env_after_init(self) -> None:
        """The async client should restore the original NO_PROXY value after init."""
        original = "localhost\n127.0.0.1"
        os.environ["NO_PROXY"] = original
        client = _DefaultAsyncHttpxClient()
        # Close the client to clean up
        import asyncio

        asyncio.run(client.aclose())
        # The original (unsanitized) value should be restored
        assert os.environ["NO_PROXY"] == original

    def test_sync_client_with_trust_env_false_no_mutation(self) -> None:
        """When trust_env=False, NO_PROXY should not be touched at all."""
        original = "localhost\n127.0.0.1"
        os.environ["NO_PROXY"] = original
        client = _DefaultHttpxClient(trust_env=False)
        client.close()
        assert os.environ["NO_PROXY"] == original

    def test_sync_client_with_clean_no_proxy(self) -> None:
        """A clean NO_PROXY value should work fine with the sync client."""
        os.environ["NO_PROXY"] = "localhost,127.0.0.1"
        client = _DefaultHttpxClient()
        client.close()
        assert os.environ["NO_PROXY"] == "localhost,127.0.0.1"
