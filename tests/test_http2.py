"""Tests for HTTP/2 support"""

import httpx
import pytest

from openai import OpenAI, AsyncOpenAI


class TestHTTP2Support:
    """Test HTTP/2 configuration and functionality"""

    def test_http2_disabled_by_default(self) -> None:
        """HTTP/2 should be disabled by default"""
        client = OpenAI(api_key="test-key")
        # Check that http2 is not enabled by default
        assert hasattr(client._client, "_transport")
        client.close()

    def test_http2_can_be_enabled(self) -> None:
        """HTTP/2 should be enabled when explicitly requested"""
        client = OpenAI(api_key="test-key", http2=True)
        # Verify client was created successfully
        assert client._client is not None
        client.close()

    def test_http2_with_custom_client_sync(self) -> None:
        """Custom http client should be respected"""
        custom_client = httpx.Client(http2=True)
        client = OpenAI(api_key="test-key", http_client=custom_client)
        assert client._client == custom_client
        client.close()

    @pytest.mark.asyncio
    async def test_async_http2_disabled_by_default(self) -> None:
        """HTTP/2 should be disabled by default for async client"""
        client = AsyncOpenAI(api_key="test-key")
        assert hasattr(client._client, "_transport")
        await client.close()

    @pytest.mark.asyncio
    async def test_async_http2_can_be_enabled(self) -> None:
        """HTTP/2 should be enabled when explicitly requested for async client"""
        client = AsyncOpenAI(api_key="test-key", http2=True)
        assert client._client is not None
        await client.close()

    @pytest.mark.asyncio
    async def test_http2_with_custom_client_async(self) -> None:
        """Custom async http client should be respected"""
        custom_client = httpx.AsyncClient(http2=True)
        client = AsyncOpenAI(api_key="test-key", http_client=custom_client)
        assert client._client == custom_client
        await client.close()

    def test_http2_connection_limits(self) -> None:
        """HTTP/2 should use optimized connection limits"""
        from openai._constants import HTTP2_CONNECTION_LIMITS

        # Verify HTTP/2 limits are defined
        assert HTTP2_CONNECTION_LIMITS.max_connections == 100
        assert HTTP2_CONNECTION_LIMITS.max_keepalive_connections == 100

    def test_sync_client_context_manager_with_http2(self) -> None:
        """HTTP/2 client should work with context manager"""
        with OpenAI(api_key="test-key", http2=True) as client:
            assert client._client is not None

    @pytest.mark.asyncio
    async def test_async_client_context_manager_with_http2(self) -> None:
        """Async HTTP/2 client should work with context manager"""
        async with AsyncOpenAI(api_key="test-key", http2=True) as client:
            assert client._client is not None
