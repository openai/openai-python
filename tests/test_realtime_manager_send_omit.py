"""Regression tests for issue #3402: Pre-connect Realtime manager.send crashes on Omit in dict events.

These tests verify that the pre-connect send() methods on both sync and async
RealtimeConnectionManager properly transform Omit values before JSON serialization,
matching the behavior of the connected send() methods.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from openai._types import omit
from openai.resources.realtime.realtime import (
    AsyncRealtimeConnectionManager,
    RealtimeConnectionManager,
)


def _make_sync_manager() -> RealtimeConnectionManager:
    """Create a minimal RealtimeConnectionManager for testing."""
    return RealtimeConnectionManager(
        client=MagicMock(),
        call_id="test-call-id",
        model="gpt-4o-realtime-preview",
        extra_query={},
        extra_headers={},
        websocket_connection_options=MagicMock(),
    )


def _make_async_manager() -> AsyncRealtimeConnectionManager:
    """Create a minimal AsyncRealtimeConnectionManager for testing."""
    return AsyncRealtimeConnectionManager(
        client=MagicMock(),
        call_id="test-call-id",
        model="gpt-4o-realtime-preview",
        extra_query={},
        extra_headers={},
        websocket_connection_options=MagicMock(),
    )


class TestRealtimeConnectionManagerSendOmit:
    """Test that RealtimeConnectionManager.send() handles Omit values."""

    def test_send_dict_with_omit_strips_omit_values(self) -> None:
        """Pre-connect send() should strip Omit values from dict events before JSON serialization."""
        manager = _make_sync_manager()

        event = {"type": "response.cancel", "event_id": omit}

        # This should NOT raise TypeError: Object of type Omit is not JSON serializable
        manager.send(event)

        # Verify the queued data has Omit stripped
        items = manager._RealtimeConnectionManager__send_queue.drain()
        assert len(items) == 1
        data = json.loads(items[0])
        assert data == {"type": "response.cancel"}
        assert "event_id" not in data

    def test_send_dict_without_omit_preserves_all_fields(self) -> None:
        """Pre-connect send() should preserve all fields when no Omit values present."""
        manager = _make_sync_manager()

        event = {"type": "response.cancel", "event_id": "evt_123"}
        manager.send(event)

        items = manager._RealtimeConnectionManager__send_queue.drain()
        assert len(items) == 1
        data = json.loads(items[0])
        assert data == {"type": "response.cancel", "event_id": "evt_123"}

    def test_send_dict_with_multiple_omit_fields(self) -> None:
        """Pre-connect send() should strip all Omit values from dict events."""
        manager = _make_sync_manager()

        event = {"type": "response.create", "event_id": omit, "response": {"modalities": omit}}
        manager.send(event)

        items = manager._RealtimeConnectionManager__send_queue.drain()
        assert len(items) == 1
        data = json.loads(items[0])
        assert data == {"type": "response.create", "response": {}}


class TestAsyncRealtimeConnectionManagerSendOmit:
    """Test that AsyncRealtimeConnectionManager.send() handles Omit values."""

    def test_send_dict_with_omit_strips_omit_values(self) -> None:
        """Pre-connect send() should strip Omit values from dict events before JSON serialization."""
        manager = _make_async_manager()

        event = {"type": "response.cancel", "event_id": omit}

        # This should NOT raise TypeError: Object of type Omit is not JSON serializable
        manager.send(event)

        # Verify the queued data has Omit stripped
        items = manager._AsyncRealtimeConnectionManager__send_queue.drain()
        assert len(items) == 1
        data = json.loads(items[0])
        assert data == {"type": "response.cancel"}
        assert "event_id" not in data

    def test_send_dict_without_omit_preserves_all_fields(self) -> None:
        """Pre-connect send() should preserve all fields when no Omit values present."""
        manager = _make_async_manager()

        event = {"type": "response.cancel", "event_id": "evt_123"}
        manager.send(event)

        items = manager._AsyncRealtimeConnectionManager__send_queue.drain()
        assert len(items) == 1
        data = json.loads(items[0])
        assert data == {"type": "response.cancel", "event_id": "evt_123"}

    def test_send_dict_with_multiple_omit_fields(self) -> None:
        """Pre-connect send() should strip all Omit values from dict events."""
        manager = _make_async_manager()

        event = {"type": "response.create", "event_id": omit, "response": {"modalities": omit}}
        manager.send(event)

        items = manager._AsyncRealtimeConnectionManager__send_queue.drain()
        assert len(items) == 1
        data = json.loads(items[0])
        assert data == {"type": "response.create", "response": {}}
