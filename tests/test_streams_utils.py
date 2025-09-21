import sys
import os
sys.path.insert(0, os.path.abspath("src"))  # Make src discoverable

import pytest
from openai._utils import _streams as streams  # Import the module

def test_consume_sync_iterator_with_none():
    """Should not raise when iterator is None"""
    streams.consume_sync_iterator(None)

@pytest.mark.asyncio
async def test_consume_async_iterator_with_none():
    """Should not raise when async iterator is None"""
    await streams.consume_async_iterator(None)
