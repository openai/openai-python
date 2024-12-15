import contextlib
import httpx
from typing import Optional, Generator
from openai import OpenAI
from openai._client import OpenAI as OpenAIClient
from openai._base_client import BaseClient

class ConnectionManager:
    """A context manager for handling OpenAI client connections."""
    
    def __init__(self):
        self._clients: list[BaseClient] = []
        
    def register_client(self, client: BaseClient) -> None:
        """Register a client for connection management."""
        self._clients.append(client)
        
    def close_all(self) -> None:
        """Close all registered client connections."""
        for client in self._clients:
            if hasattr(client, '_client') and isinstance(client._client, httpx.Client):
                client._client.close()
        self._clients.clear()
        
    def __enter__(self) -> 'ConnectionManager':
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close_all()

# Global connection manager instance
_connection_manager = ConnectionManager()

class ManagedOpenAI(OpenAI):
    """OpenAI client with automatic connection management."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        _connection_manager.register_client(self)
        
    def __enter__(self) -> 'ManagedOpenAI':
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if hasattr(self, '_client') and isinstance(self._client, httpx.Client):
            self._client.close()

@contextlib.contextmanager
def managed_client(**kwargs) -> Generator[OpenAI, None, None]:
    """Context manager for creating and automatically closing OpenAI clients."""
    client = ManagedOpenAI(**kwargs)
    try:
        yield client
    finally:
        if hasattr(client, '_client') and isinstance(client._client, httpx.Client):
            client._client.close()

def get_managed_client(**kwargs) -> ManagedOpenAI:
    """Create a new managed OpenAI client instance."""
    return ManagedOpenAI(**kwargs)