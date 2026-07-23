"""Thread-safe TypeAdapter cache with bounded size."""

from __future__ import annotations

import threading
from typing import Any, TypeVar, Generic
from functools import lru_cache
from pydantic import TypeAdapter

T = TypeVar('T')

# Use a bounded cache instead of unbounded
_MAX_CACHE_SIZE = 128

# Thread-local storage for type adapters to prevent hash conflicts
_thread_local = threading.local()


def get_type_adapter(type_: type[T]) -> TypeAdapter[T]:
    """
    Get a TypeAdapter instance for the given type.
    
    Uses a thread-safe, bounded cache to prevent memory leaks
    in multi-threaded environments.
    
    Args:
        type_: The type to create an adapter for
        
    Returns:
        A TypeAdapter instance for the given type
    """
    # Get or create thread-local cache
    if not hasattr(_thread_local, 'adapter_cache'):
        _thread_local.adapter_cache = {}
    
    cache = _thread_local.adapter_cache
    
    # Use the fully qualified name as key instead of the type object itself
    # This avoids hash conflicts from dynamically generated generic types
    cache_key = _get_type_cache_key(type_)
    
    if cache_key not in cache:
        # Implement LRU eviction if cache is too large
        if len(cache) >= _MAX_CACHE_SIZE:
            # Remove oldest item (simple FIFO for thread-local cache)
            first_key = next(iter(cache))
            del cache[first_key]
        
        cache[cache_key] = TypeAdapter(type_)
    
    return cache[cache_key]


def _get_type_cache_key(type_: Any) -> str:
    """
    Generate a stable cache key for a type.
    
    Uses type name and module information to create a key that
    remains consistent across type recreations.
    
    Args:
        type_: The type to generate a key for
        
    Returns:
        A string key that uniquely identifies the type
    """
    try:
        # For generic types, extract the origin and args
        if hasattr(type_, '__origin__'):
            origin = type_.__origin__
            args = getattr(type_, '__args__', ())
            
            origin_key = f"{origin.__module__}.{origin.__qualname__}"
            args_keys = ','.join(_get_type_cache_key(arg) for arg in args)
            
            return f"{origin_key}[{args_keys}]"
        else:
            # For regular types
            return f"{type_.__module__}.{type_.__qualname__}"
    except (AttributeError, TypeError):
        # Fallback to repr for complex types
        return repr(type_)


# Alternative implementation using a global bounded LRU cache with locks
_cache_lock = threading.Lock()

@lru_cache(maxsize=_MAX_CACHE_SIZE)
def get_type_adapter_global(type_key: str, type_: type[T]) -> TypeAdapter[T]:
    """
    Global cached TypeAdapter factory with bounded size.
    
    This is thread-safe but uses a global cache.
    Use get_type_adapter() for better thread isolation.
    """
    return TypeAdapter(type_)


def get_type_adapter_with_lock(type_: type[T]) -> TypeAdapter[T]:
    """
    Get a TypeAdapter using a global cache with explicit locking.
    
    Args:
        type_: The type to create an adapter for
        
    Returns:
        A TypeAdapter instance for the given type
    """
    cache_key = _get_type_cache_key(type_)
    
    with _cache_lock:
        return get_type_adapter_global(cache_key, type_)
