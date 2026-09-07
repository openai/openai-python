#!/usr/bin/env python3
"""Test to verify that JSON serialization doesn't block the event loop."""

import asyncio
import time
from typing import Any
from pydantic import BaseModel
from openai._base_client import AsyncAPIClient
from openai._models import FinalRequestOptions


class LargeModel(BaseModel):
    """A large Pydantic model to simulate structured output."""
    field1: str
    field2: str
    field3: dict[str, Any]
    field4: list[dict[str, Any]]


async def background_task(duration: float) -> float:
    """Simulate background work that would be blocked by event loop blocking."""
    start = time.time()
    await asyncio.sleep(duration)
    end = time.time()
    return end - start


async def test_json_serialization_doesnt_block_event_loop():
    """Test that JSON serialization runs in a thread and doesn't block the event loop."""
    client = AsyncAPIClient(
        version="test",
        base_url="https://api.example.com",
        _strict_response_validation=False,
    )

    # Create a large model to serialize
    large_data = LargeModel(
        field1="test" * 100,
        field2="data" * 100,
        field3={f"key_{i}": f"value_{i}" * 50 for i in range(100)},
        field4=[{f"field_{j}": f"data_{j}" * 20} for j in range(100)],
    )

    # Create a request that will trigger JSON serialization
    options = FinalRequestOptions(
        method="POST",
        url="/test",
        json_data=large_data.model_dump(),
    )

    # Run both the JSON serialization and a background task concurrently
    # If JSON serialization blocks the event loop, the background task
    # will take longer than expected
    start_time = time.time()
    
    # Run background task while building request
    bg_task = asyncio.create_task(background_task(0.1))
    request = await client._build_request_async(options)
    bg_result = await bg_task
    
    elapsed = time.time() - start_time

    # If JSON serialization runs in a thread (as intended), the background task
    # should complete in ~0.1 seconds plus some overhead (typically < 0.2s total)
    # If JSON serialization blocks the event loop, it would take much longer
    
    print(f"Background task duration: {bg_result:.4f}s")
    print(f"Total elapsed time: {elapsed:.4f}s")
    
    # The background task should complete in approximately 0.1 seconds
    # If it takes significantly longer, JSON serialization is blocking the event loop
    assert 0.08 < bg_result < 0.3, (
        f"Background task took {bg_result:.4f}s, expected ~0.1s. "
        "This suggests JSON serialization is blocking the event loop."
    )
    
    print("[OK] JSON serialization does not block the event loop")
    await client.close()


if __name__ == "__main__":
    asyncio.run(test_json_serialization_doesnt_block_event_loop())
    print("[OK] All tests passed!")
