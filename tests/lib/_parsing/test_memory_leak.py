import gc
from typing import List

import pytest
from pydantic import Field, create_model

from openai.lib._parsing import type_to_response_format_param
from openai.lib._parsing._completions import _schema_cache


@pytest.mark.asyncio
async def test_async_completions_parse_memory():
    """Test if AsyncCompletions.parse() doesn't leak memory with dynamic models"""
    StepModel = create_model(
        "Step",
        explanation=(str, Field()),
        output=(str, Field()),
    )
    
    # Clear the cache and record initial state
    _schema_cache.clear()
    initial_cache_size = len(_schema_cache)
    
    # Simulate the issue by creating multiple models and making calls
    models = []
    for i in range(10):
        # Create a new dynamic model each time
        new_model = create_model(
            f"MathResponse{i}",
            steps=(List[StepModel], Field()),
            final_answer=(str, Field()),
        )
        models.append(new_model)
        
        # Convert to response format and check if it's in the cache
        type_to_response_format_param(new_model)
        assert new_model in _schema_cache
    
    # Record cache size with all models referenced
    cache_size_with_references = len(_schema_cache)
    
    # Let the models go out of scope and trigger garbage collection
    models = None
    gc.collect()
    
    # After garbage collection, the cache should be significantly reduced
    cache_size_after_gc = len(_schema_cache)
    assert cache_size_after_gc < cache_size_with_references
    # The cache size should be close to the initial size (with some tolerance)
    assert cache_size_after_gc < cache_size_with_references / 2