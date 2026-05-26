# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import pytest

from openai._exceptions import WebSocketQueueFullError
from openai._send_queue import SendQueue


class TestSendQueue:
    def test_enqueue_and_drain(self) -> None:
        q = SendQueue()
        q.enqueue('{"type": "session.update"}')
        q.enqueue('{"type": "response.create"}')
        assert len(q) == 2

        items = q.drain()
        assert items == ['{"type": "session.update"}', '{"type": "response.create"}']
        assert len(q) == 0

    def test_enqueue_respects_byte_limit(self) -> None:
        q = SendQueue(max_bytes=10)
        q.enqueue("12345")  # 5 bytes, fits
        with pytest.raises(WebSocketQueueFullError):
            q.enqueue("123456")  # 6 bytes, would exceed 10
        assert len(q) == 1

    def test_drain_empties_queue(self) -> None:
        q = SendQueue()
        q.enqueue("hello")
        q.drain()
        assert len(q) == 0
        assert not q

    def test_bool(self) -> None:
        q = SendQueue()
        assert not q
        q.enqueue("x")
        assert q

    def test_flush_sync(self) -> None:
        q = SendQueue()
        q.enqueue("a")
        q.enqueue("b")
        q.enqueue("c")

        sent: list[str] = []
        q.flush_sync(sent.append)
        assert sent == ["a", "b", "c"]
        assert len(q) == 0

    def test_flush_sync_requeues_on_failure(self) -> None:
        q = SendQueue()
        q.enqueue("a")
        q.enqueue("b")
        q.enqueue("c")

        sent: list[str] = []

        def failing_send(data: str) -> None:
            if data == "b":
                raise RuntimeError("send failed")
            sent.append(data)

        with pytest.raises(RuntimeError, match="send failed"):
            q.flush_sync(failing_send)

        assert sent == ["a"]
        # b and c should be re-queued
        remaining = q.drain()
        assert remaining == ["b", "c"]

    @pytest.mark.asyncio
    async def test_flush_async(self) -> None:
        q = SendQueue()
        q.enqueue("a")
        q.enqueue("b")

        sent: list[str] = []

        async def async_send(data: str) -> None:
            sent.append(data)

        await q.flush_async(async_send)
        assert sent == ["a", "b"]
        assert len(q) == 0

    @pytest.mark.asyncio
    async def test_flush_async_requeues_on_failure(self) -> None:
        q = SendQueue()
        q.enqueue("a")
        q.enqueue("b")
        q.enqueue("c")

        sent: list[str] = []

        async def failing_send(data: str) -> None:
            if data == "b":
                raise RuntimeError("send failed")
            sent.append(data)

        with pytest.raises(RuntimeError, match="send failed"):
            await q.flush_async(failing_send)

        assert sent == ["a"]
        remaining = q.drain()
        assert remaining == ["b", "c"]

    def test_flush_sync_preserves_new_items_on_failure(self) -> None:
        """If items are enqueued after flush starts and flush fails,
        the re-queued items should come before the new items."""
        q = SendQueue()
        q.enqueue("a")
        q.enqueue("b")

        def failing_send(data: str) -> None:
            if data == "b":
                # Simulate another thread enqueuing during flush
                q.enqueue("new")
                raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            q.flush_sync(failing_send)

        # "b" (failed) should come before "new" (added during flush)
        remaining = q.drain()
        assert remaining == ["b", "new"]
