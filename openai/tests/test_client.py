import pytest

import openai.client

@pytest.fixture
def clear_oai_module(monkeypatch: pytest.MonkeyPatch):
    for key in [ 'api_base', 'api_key', 'api_type', 'api_version']:
        ...
    monkeypatch.setattr(openai, 'api_base', "https://api.openai.com/v1")
    monkeypatch.setattr(openai, 'api_key', None)
    monkeypatch.setattr(openai, 'api_type', "open_ai")
    monkeypatch.setattr(openai, 'api_version', None)

def setup_oai_module(monkeypatch: pytest.MonkeyPatch, **kwargs):
    for n, v in kwargs.items():
        monkeypatch.setattr(openai, n, v)
        
def test_construct_client(monkeypatch: pytest.MonkeyPatch, clear_oai_module):
    setup_oai_module(monkeypatch, api_key=None)
    client = openai.client.OpenAIClient()
    assert client.api_base == openai.api_base
    assert client.api_type == openai.api_type
    assert client.auth.get_token() is None

def test_construct_azure_client(monkeypatch: pytest.MonkeyPatch, clear_oai_module):
    setup_oai_module(monkeypatch, api_key=None, api_base='something different')

    provided_api_base = 'https://contoso.microsoft.com'
    client = openai.client.OpenAIClient(api_base=provided_api_base, backend='azure')
    assert client.api_base == provided_api_base
    assert client.api_type == 'azure'
    assert client.auth.get_token() is None

def test_construct_azure_client_aad(monkeypatch: pytest.MonkeyPatch, clear_oai_module):
    provided_api_base = 'https://contoso.microsoft.com'
    def mock_get_token(*args, **kwargs):
        return 'expected token'
    monkeypatch.setattr(openai.client.AzureTokenAuth, 'get_token', mock_get_token)

    client = openai.client.OpenAIClient(api_base=provided_api_base, backend='azure', auth=openai.client.AzureTokenAuth(credential='dummy'))
    assert client.api_base == provided_api_base
    assert client.api_type == 'azure_ad'
    assert client.auth.get_token() == 'expected token'

def test_construct_azure_client_api_key(monkeypatch: pytest.MonkeyPatch, clear_oai_module):
    provided_api_base = 'https://contoso.microsoft.com'
    client = openai.client.OpenAIClient(api_base=provided_api_base, backend='azure', auth='secret key')
    assert client.api_base == provided_api_base
    assert client.api_type == 'azure'
    assert client.auth.get_token() == 'secret key'

def test_construct_openai_client_api_key():
    client = openai.client.OpenAIClient(auth='secret key')
    assert client.api_base == openai.api_base
    assert client.api_type == 'open_ai'
    assert client.auth.get_token() == 'secret key'

@pytest.fixture
def embedding_response():
    return   {
                "object": "list",
                "data": [
                    {
                    "object": "embedding",
                    "embedding": [
                        0.0023064255,
                        -0.009327292,
                        -0.0028842222,
                    ],
                    "index": 0
                    }
                ],
                "model": "text-embedding-ada-002",
                "usage": {
                    "prompt_tokens": 8,
                    "total_tokens": 8
                }
        }

def test_make_call_client_aad(monkeypatch: pytest.MonkeyPatch, clear_oai_module, embedding_response):
    provided_api_base = 'https://contoso.microsoft.com'
    def mock_get_token(*args, **kwargs):
        return 'expected token'
    
    def mock_embeddings_response(*args, **kwargs):
        assert kwargs.get('deployment_id') == 'das deployment'
        assert kwargs.get('api_version') == openai.client.LATEST_AZURE_API_VERSION
        assert kwargs.get('api_type') == 'azure_ad'
        return embedding_response

    monkeypatch.setattr(openai.client.AzureTokenAuth, 'get_token', mock_get_token)
    monkeypatch.setattr(openai.Embedding, 'create', mock_embeddings_response)

    client = openai.client.OpenAIClient(backend='azure', api_base = provided_api_base, auth=openai.client.AzureTokenAuth(credential='dummy'))
    client.embeddings("some data", model='das deployment')


def test_make_call_client_azure_key(monkeypatch: pytest.MonkeyPatch, clear_oai_module, embedding_response):
    provided_api_base = 'https://contoso.microsoft.com'
    def mock_get_token(*args, **kwargs):
        return 'expected token'
    def mock_embeddings_response(*args, **kwargs):
        assert kwargs.get('deployment_id') == 'das deployment'
        assert kwargs.get('api_version') == openai.client.LATEST_AZURE_API_VERSION
        assert kwargs.get('api_type') == 'azure'
        assert kwargs.get('api_key', 'secret key')
        return embedding_response
    
    monkeypatch.setattr(openai.client.AzureTokenAuth, 'get_token', mock_get_token)
    monkeypatch.setattr(openai.Embedding, 'create', mock_embeddings_response)

    client = openai.client.OpenAIClient(backend='azure', api_base = provided_api_base, auth="secret key")
    client.embeddings("some data", model='das deployment')


def test_make_call_client_oai_key(monkeypatch: pytest.MonkeyPatch, clear_oai_module, embedding_response):
    provided_api_base = 'https://contoso.microsoft.com'
    def mock_get_token(*args, **kwargs):
        return 'expected token'
    def mock_embeddings_response(*args, **kwargs):
        assert kwargs.get('model') == 'das model'
        assert kwargs.get('api_type') == 'open_ai'
        assert kwargs.get('api_key', 'secret key')
        return embedding_response
    
    monkeypatch.setattr(openai.client.AzureTokenAuth, 'get_token', mock_get_token)
    monkeypatch.setattr(openai.Embedding, 'create', mock_embeddings_response)

    client = openai.client.OpenAIClient(auth="secret key")
    client.embeddings("some data", model='das model')