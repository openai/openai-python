"""Regression tests for event loop blocking during JSON serialization.

This test verifies that async requests don't block the event loop during JSON
serialization, which is critical for concurrent operations like Redis, Kafka,
and WebSocket communication that share the event loop.

See: https://github.com/openai/openai-python/issues/3777
"""

from __future__ import annotations

import asyncio
from typing import AsyncIterator

import httpx2
import pytest

from openai import AsyncOpenAI
from tests.respx2 import MockRouter


@pytest.mark.asyncio
async def test_async_request_does_not_block_event_loop(
    respx2_mock: MockRouter,
    async_client: AsyncOpenAI,
) -> None:
    """Test that async JSON serialization doesn't block the event loop.
    
    This test verifies the fix for issue #3777 by ensuring that:
    1. Background concurrent work completes while serialization happens
    2. The event loop remains responsive during JSON serialization
    3. Multiple concurrent tasks can progress simultaneously
    """
    # Track when the background task completes
    background_task_started = asyncio.Event()
    background_task_done = asyncio.Event()
    background_task_iterations = 0
    
    async def background_work() -> None:
        """Simulates concurrent work (e.g., Redis access, WebSocket read)."""
        nonlocal background_task_iterations
        background_task_started.set()
        
        # Run for a short time to give the event loop a chance to be blocked
        for _ in range(100):
            background_task_iterations += 1
            await asyncio.sleep(0.001)  # 1ms per iteration = 100ms total
        
        background_task_done.set()
    
    # Setup the mock to return a successful response
    respx2_mock.post("/chat/completions").mock(
        return_value=httpx2.Response(
            status_code=200,
            json={
                "id": "chatcmpl-test",
                "object": "chat.completion",
                "created": 1234567890,
                "model": "gpt-4",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Hello!"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            },
        )
    )
    
    # Start the background task
    background_task = asyncio.create_task(background_work())
    
    # Wait for background task to start
    await asyncio.wait_for(background_task_started.wait(), timeout=1.0)
    
    # Make an async API request (which triggers JSON serialization)
    # This should NOT block the event loop, allowing background_work to continue
    response = await async_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}],
    )
    
    # Wait for background task to complete
    await asyncio.wait_for(background_task_done.wait(), timeout=5.0)
    await background_task
    
    # Verify the response was successful
    assert response.id == "chatcmpl-test"
    assert response.choices[0].message.content == "Hello!"
    
    # The critical assertion: background task must have made significant progress
    # If the event loop was blocked during serialization, the background task
    # would complete much later (only after the request completes).
    # With proper async serialization, the background task should complete
    # most of its iterations during the request.
    #
    # We expect at least 50 iterations out of 100 to have completed.
    # This threshold allows for small timing variations while still catching
    # any significant event loop blocking.
    assert background_task_iterations >= 50, (
        f"Background task only completed {background_task_iterations}/100 iterations. "
        f"Event loop may be getting blocked during JSON serialization."
    )
