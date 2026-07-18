"""Tests to verify that destructor exception handlers log errors instead of silently swallowing them."""

from __future__ import annotations

import gc
import logging
from unittest import mock

import httpx
import pytest

from openai._base_client import SyncHttpxClientWrapper, AsyncHttpxClientWrapper


class TestSyncDestructorLogging:
    """Test that SyncHttpxClientWrapper.__del__ logs exceptions instead of silently swallowing them."""

    def test_del_logs_on_close_error(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that __del__ logs when close() raises an exception."""
        client = SyncHttpxClientWrapper()

        # Mock close() to raise an exception
        with mock.patch.object(client, "close", side_effect=RuntimeError("close failed")):
            with caplog.at_level(logging.DEBUG, logger="openai._base_client"):
                client.__del__()

        assert any(
            "Failed to close client in destructor" in record.message
            for record in caplog.records
        ), f"Expected log message not found in: {[r.message for r in caplog.records]}"

    def test_del_no_log_on_success(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that __del__ doesn't log when close() succeeds."""
        client = SyncHttpxClientWrapper()

        with caplog.at_level(logging.DEBUG, logger="openai._base_client"):
            client.__del__()

        assert not any(
            "Failed to close client in destructor" in record.message
            for record in caplog.records
        )

    def test_del_skips_if_closed(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that __del__ skips close() if already closed."""
        client = SyncHttpxClientWrapper()
        client.close()

        with mock.patch.object(client, "close") as mock_close:
            with caplog.at_level(logging.DEBUG, logger="openai._base_client"):
                client.__del__()

        mock_close.assert_not_called()


class TestAsyncDestructorLogging:
    """Test that AsyncHttpxClientWrapper.__del__ logs exceptions instead of silently swallowing them."""

    def test_del_logs_when_no_event_loop(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that __del__ logs when asyncio.get_running_loop() raises (no event loop)."""
        client = AsyncHttpxClientWrapper()

        with mock.patch("asyncio.get_running_loop", side_effect=RuntimeError("no running event loop")):
            with caplog.at_level(logging.DEBUG, logger="openai._base_client"):
                client.__del__()
                # Mark as closed so GC won't trigger __del__ again
                client._state = httpx._client.ClientState.CLOSED

        assert any(
            "Failed to close async client in destructor" in record.message
            for record in caplog.records
        ), f"Expected log message not found in: {[r.message for r in caplog.records]}"

    def test_del_no_log_on_success(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that __del__ doesn't log when it successfully creates a close task."""
        client = AsyncHttpxClientWrapper()

        mock_loop = mock.MagicMock()
        with mock.patch("asyncio.get_running_loop", return_value=mock_loop):
            with caplog.at_level(logging.DEBUG, logger="openai._base_client"):
                client.__del__()
                # Mark as closed so GC won't trigger __del__ again
                client._state = httpx._client.ClientState.CLOSED

        assert not any(
            "Failed to close async client in destructor" in record.message
            for record in caplog.records
        ), f"Unexpected log messages: {[r.message for r in caplog.records]}"

    def test_del_skips_if_closed(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that __del__ skips if already closed."""
        client = AsyncHttpxClientWrapper()
        client._state = httpx._client.ClientState.CLOSED

        with mock.patch("asyncio.get_running_loop") as mock_loop:
            with caplog.at_level(logging.DEBUG, logger="openai._base_client"):
                client.__del__()

        mock_loop.assert_not_called()
