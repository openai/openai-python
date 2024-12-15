import pytest
from openai.connection_manager import ConnectionManager, ManagedOpenAI, managed_client, get_managed_client

def test_connection_manager_context():
    with ConnectionManager() as manager:
        client = get_managed_client(api_key="test_key")
        assert client in manager._clients
    assert len(manager._clients) == 0

def test_managed_client_context():
    with managed_client(api_key="test_key") as client:
        assert isinstance(client, ManagedOpenAI)
        assert hasattr(client, '_client')

def test_get_managed_client():
    client = get_managed_client(api_key="test_key")
    assert isinstance(client, ManagedOpenAI)
    if hasattr(client, '_client'):
        client._client.close()