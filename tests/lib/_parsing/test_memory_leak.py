import unittest
import gc
import sys
from unittest.mock import AsyncMock, patch, MagicMock
from typing import List

import pytest
from pydantic import Field, create_model

from openai.resources.beta.chat.completions import AsyncCompletions
from openai.lib._parsing import type_to_response_format_param
from openai.lib._parsing._completions import _schema_cache

class TestMemoryLeak(unittest.TestCase):
    def setUp(self):
        # Clear the schema cache before each test
        _schema_cache.clear()
        
    def test_schema_cache_with_models(self):
        """Test if schema cache properly handles dynamic models and prevents memory leak"""
        
        StepModel = create_model(
            "Step",
            explanation=(str, Field()),
            output=(str, Field()),
        )
        
        # Create several models and ensure they're cached properly
        models = []
        for i in range(5):
            model = create_model(
                f"MathResponse{i}",
                steps=(List[StepModel], Field()),
                final_answer=(str, Field()),
            )
            models.append(model)
            
            # Convert model to response format param
            param = type_to_response_format_param(model)
            
            # Check if the model is in the cache
            self.assertIn(model, _schema_cache)
        
        # Test that all models are in the cache
        self.assertEqual(len(_schema_cache), 5)
        
        # Let the models go out of scope and trigger garbage collection
        models = None
        gc.collect()
        
        # After garbage collection, the cache should be empty or reduced
        # since we're using weakref.WeakKeyDictionary
        self.assertLess(len(_schema_cache), 5)

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
    
    # Create a mock client 
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock()
    
    # Create the AsyncCompletions instance with our mock client
    completions = AsyncCompletions(mock_client)
    
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