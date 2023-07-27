import os
import sys

from typing import Union
if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

import pytest
import openai.client

# Live tests
API_TYPE = ["azure", "openai", "azuredefault"]
API_BASE = os.environ["AZURE_API_BASE"]
AZURE_API_KEY = os.environ["AZURE_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_KEY"]
API_VERSION  = "2023-07-01-preview"
COMPLETION_MODEL = "text-davinci-003"
CHAT_COMPLETION_MODEL = "gpt-35-turbo"
CHAT_COMPLETION_MODEL_OPENAI = "gpt-3.5-turbo"
EMBEDDINGS_MODEL = "text-embedding-ada-002"
IMAGE_PATH = ""
MASK_IMAGE_PATH = ""
AUDIO_FILE_PATH = ""


@pytest.fixture
def client(api_type):
    if api_type == "azure":
        client = openai.client.OpenAIClient(
            api_base=API_BASE,
            auth=AZURE_API_KEY,
            api_version=API_VERSION,
            backend="azure"
        )
    elif api_type == "azuredefault":
        api_type = "azure"
        client = openai.client.OpenAIClient(
            api_base=API_BASE,
            auth="azuredefault",
            api_version=API_VERSION,
            backend="azure"
        )
    elif api_type == "openai":
        client = openai.client.OpenAIClient(
            auth=OPENAI_API_KEY,
            backend="openai"
        )

    return client


@pytest.fixture
def clear_oai_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(openai, 'api_base', "https://api.openai.com/v1")
    monkeypatch.setattr(openai, 'api_key', None)
    monkeypatch.setattr(openai, 'api_type', "open_ai")
    monkeypatch.setattr(openai, 'api_version', None)
    monkeypatch.setattr(openai, 'organization', None)

def setup_oai_module(monkeypatch: pytest.MonkeyPatch, **kwargs):
    for n, v in kwargs.items():
        monkeypatch.setattr(openai, n, v)

# MOCK TESTS ------------------------------------------------
        
@pytest.mark.usefixtures("clear_oai_module")
def test_construct_client(monkeypatch: pytest.MonkeyPatch):
    setup_oai_module(monkeypatch, api_key=None)
    client = openai.client.OpenAIClient()
    assert client.api_base == openai.api_base
    assert client.api_type == openai.api_type
    assert client.auth.get_token() is None

@pytest.mark.usefixtures("clear_oai_module")
def test_construct_azure_client(monkeypatch: pytest.MonkeyPatch):
    setup_oai_module(monkeypatch, api_key=None, api_base='something different')

    provided_api_base = 'https://contoso.microsoft.com'
    client = openai.client.OpenAIClient(api_base=provided_api_base, backend='azure')
    assert client.api_base == provided_api_base
    assert client.api_type == 'azure'
    assert client.auth.get_token() is None

@pytest.mark.usefixtures("clear_oai_module")
def test_construct_azure_client_aad(monkeypatch: pytest.MonkeyPatch):
    provided_api_base = 'https://contoso.microsoft.com'
    def mock_get_token(*args, **kwargs):
        return 'expected token'
    monkeypatch.setattr(openai.client.AzureTokenAuth, 'get_token', mock_get_token)

    client = openai.client.OpenAIClient(api_base=provided_api_base, backend='azure', auth=openai.client.AzureTokenAuth(credential='dummy'))
    assert client.api_base == provided_api_base
    assert client.api_type == 'azure_ad'
    assert client.auth.get_token() == 'expected token'

@pytest.mark.usefixtures("clear_oai_module")
def test_construct_azure_client_api_key(monkeypatch: pytest.MonkeyPatch):
    provided_api_base = 'https://contoso.microsoft.com'
    client = openai.client.OpenAIClient(api_base=provided_api_base, backend='azure', auth='secret key')
    assert client.api_base == provided_api_base
    assert client.api_type == 'azure'
    assert client.auth.get_token() == 'secret key'

def test_construct_openai_client_api_key():
    client = openai.client.OpenAIClient(auth='secret key', organization="my org")
    assert client.api_base == openai.api_base
    assert client.api_type == 'open_ai'
    assert client.organization == "my org"
    assert client.auth.get_token() == 'secret key'

@pytest.mark.usefixtures("clear_oai_module")
def test_make_call_client_aad(monkeypatch: pytest.MonkeyPatch):
    provided_api_base = 'https://contoso.microsoft.com'
    def mock_get_token(*args, **kwargs):
        return 'expected token'
    
    def mock_embeddings_response(*args, **kwargs):
        return args, kwargs

    monkeypatch.setattr(openai.client.AzureTokenAuth, 'get_token', mock_get_token)
    monkeypatch.setattr(openai.Embedding, 'create', mock_embeddings_response)

    client = openai.client.OpenAIClient(backend='azure', api_base = provided_api_base, auth=openai.client.AzureTokenAuth(credential='dummy'))
    args, kwargs = client.embeddings("some data", model='das deployment')

    assert kwargs.get('deployment_id') == 'das deployment'
    assert kwargs.get('api_version') == openai.client.LATEST_AZURE_API_VERSION
    assert kwargs.get('api_type') == 'azure_ad'

@pytest.mark.usefixtures("clear_oai_module")
def test_make_call_client_azure_key(monkeypatch: pytest.MonkeyPatch):
    provided_api_base = 'https://contoso.microsoft.com'
    def mock_get_token(*args, **kwargs):
        return 'expected token'
    def mock_embeddings_response(*args, **kwargs):
        return args, kwargs
    
    monkeypatch.setattr(openai.client.AzureTokenAuth, 'get_token', mock_get_token)
    monkeypatch.setattr(openai.Embedding, 'create', mock_embeddings_response)

    client = openai.client.OpenAIClient(backend='azure', api_base = provided_api_base, auth="secret key")
    args, kwargs = client.embeddings("some data", model='das deployment')

    assert kwargs.get('deployment_id') == 'das deployment'
    assert kwargs.get('api_version') == openai.client.LATEST_AZURE_API_VERSION
    assert kwargs.get('api_type') == 'azure'
    assert kwargs.get('api_key', 'secret key')

@pytest.mark.usefixtures("clear_oai_module")
def test_make_call_client_oai_key(monkeypatch: pytest.MonkeyPatch):
    provided_api_base = 'https://contoso.microsoft.com'
    def mock_get_token(*args, **kwargs):
        return 'expected token'
    def mock_embeddings_response(*args, **kwargs):
        return args, kwargs
    
    monkeypatch.setattr(openai.client.AzureTokenAuth, 'get_token', mock_get_token)
    monkeypatch.setattr(openai.Embedding, 'create', mock_embeddings_response)

    client = openai.client.OpenAIClient(auth="secret key")
    client.embeddings("some data", model='das model')


def test_populate_args():
    client = openai.client.OpenAIClient()

    # valid override
    kwargs = {
        "api_base": "expected",
        "api_key": "expected",
        "api_version": "expected",
        "prompt": "expected",
    }

    overrides = {
        "temperature": 0.1
    }

    client._populate_args(kwargs, **overrides)

    assert kwargs == {
        "api_base": "expected",
        "api_key": "expected",
        "api_type": "open_ai",
        "api_version": "expected",
        "prompt": "expected",
        "organization": None,
        "temperature": 0.1
    }


    # unexpected override by user
    kwargs = {
        "prompt": "expected",
        "api_base": "expected",
        "api_key": "expected",
        "api_type": "expected",
        "api_version": "expected",
        "organization": "expected",
        "stream": True
    }

    overrides = {
        "stream": False
    }

    with pytest.raises(TypeError):
        client._populate_args(kwargs, **overrides)

    # attempt to change api_base on per-method call
    kwargs = {
        "prompt": "expected",
        "api_base": "expected",
        "api_key": "expected",
        "api_type": "expected",
        "api_version": "expected",
        "organization": "expected",
        "stream": True
    }

    overrides = {
        "api_base": "update",
    }

    with pytest.raises(TypeError):
        client._populate_args(kwargs, **overrides)


def test_normalize_model():
    client = openai.client.OpenAIClient(backend="azure", api_base="azurebase")

    # azure: deployment_id --> deployment_id
    kwargs = {"deployment_id": "ada"}
    client._normalize_model(kwargs)
    assert kwargs == {"deployment_id": "ada"}

    # azure: engine --> engine
    kwargs = {"engine": "ada"}
    client._normalize_model(kwargs)
    assert kwargs == {"engine": "ada"}

    # azure: model --> deployment_id (normalized)
    kwargs = {"model": "ada"}
    client._normalize_model(kwargs)
    assert kwargs == {"deployment_id": "ada"}

    client = openai.client.OpenAIClient(backend="openai")
    # openai: deployment_id --> exception
    kwargs = {"deployment_id": "ada"}
    client._normalize_model(kwargs)
    # incorrect arg raised by library
    assert kwargs == {"deployment_id": "ada"}

    # openai: engine --> engine
    kwargs = {"engine": "ada"}
    client._normalize_model(kwargs)
    assert kwargs == {"engine": "ada"}

    # openai: model --> model
    kwargs = {"model": "ada"}
    client._normalize_model(kwargs)
    assert kwargs == {"model": "ada"}

    # too many args
    kwargs = {"model": "ada", "deployment_id": "ada"}
    with pytest.raises(TypeError):
        client._normalize_model(kwargs)


# LIVE TESTS ------------------------------------------------
# COMPLETION TESTS
@pytest.mark.parametrize("api_type", API_TYPE)
def test_client_completion(client):
    completion = client.completion(
        prompt="hello world",
        model=COMPLETION_MODEL
    )
    assert completion


@pytest.mark.parametrize("api_type", API_TYPE)
def test_client_completion_stream(client):
    completion = client.iter_completion(
        prompt="hello world",
        model=COMPLETION_MODEL
    )
    for c in completion:
        assert c

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", API_TYPE)
async def test_client_acompletion(client):
    completion = await client.acompletion(
        prompt="hello world",
        model=COMPLETION_MODEL
    )
    assert completion

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", API_TYPE)
async def test_client_acompletion_stream(client):
    completion = await client.aiter_completion(
        prompt="hello world",
        model=COMPLETION_MODEL
    )
    async for c in completion:
        assert c


# CHAT COMPLETION TESTS
@pytest.mark.parametrize("api_type", API_TYPE)
def test_client_chatcompletion(client):
    chat_completion = client.chatcompletion(
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ],
        model=CHAT_COMPLETION_MODEL if client.backend == "azure" else CHAT_COMPLETION_MODEL_OPENAI
    )
    assert chat_completion

@pytest.mark.parametrize("api_type", API_TYPE)
def test_client_chat_completion_stream(client):
    chat_completion = client.iter_chatcompletion(
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ],
        model=CHAT_COMPLETION_MODEL if client.backend == "azure" else CHAT_COMPLETION_MODEL_OPENAI
    )
    for c in chat_completion:
        assert c

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", API_TYPE)
async def test_client_achatcompletion(client):
    chat_completion = await client.achatcompletion(
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ],
        model=CHAT_COMPLETION_MODEL if client.backend == "azure" else CHAT_COMPLETION_MODEL_OPENAI
    )
    assert chat_completion

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", API_TYPE)
async def test_client_achat_completion_stream(client):
    chat_completion = await client.aiter_chatcompletion(
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ],
        model=CHAT_COMPLETION_MODEL if client.backend == "azure" else CHAT_COMPLETION_MODEL_OPENAI
    )
    async for c in chat_completion:
        assert c


# EMBEDDING TESTS
@pytest.mark.parametrize("api_type", API_TYPE)
def test_client_embeddings(client):
    embeddings = client.embeddings(
        input="hello world",
        model=EMBEDDINGS_MODEL
    )
    assert embeddings

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", API_TYPE)
async def test_client_aembeddings(client):
    embeddings = await client.aembeddings(
        input="hello world",
        model=EMBEDDINGS_MODEL
    )
    assert embeddings


# IMAGE CREATE TESTS
@pytest.mark.parametrize("api_type", API_TYPE)
def test_client_image_create(client):
    image = client.image(
        prompt="A cute baby sea otter",
        n=1
    )
    assert image

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", API_TYPE)
async def test_client_aimage_create(client):
    image = await client.aimage(
        prompt="A cute baby sea otter",
        n=1
    )
    assert image


# IMAGE VARIATION TESTS
@pytest.mark.parametrize("api_type", ["openai"])
def test_client_image_variation(client):
    variation = client.image_variation(
        image=open(IMAGE_PATH, "rb"),
        n=2,
        size="1024x1024"
    )
    assert variation

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", ["openai"])
async def test_client_aimage_variation(client):
    variation = await client.aimage_variation(
        image=open(IMAGE_PATH, "rb"),
        n=2,
        size="1024x1024"
    )
    assert variation

# IMAGE EDIT TESTS
@pytest.mark.parametrize("api_type", ["openai"])
def test_client_image_edit(client):
    edit = client.image_edit(
        image=open(IMAGE_PATH, "rb"),
        mask=open(MASK_IMAGE_PATH, "rb"),
        prompt="A cute baby sea otter wearing a beret",
        n=2,
        size="1024x1024"
    )
    assert edit

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", ["openai"])
async def test_client_aimage_edit(client):
    edit = await client.aimage_edit(
        image=open(IMAGE_PATH, "rb"),
        mask=open(MASK_IMAGE_PATH, "rb"),
        prompt="A cute baby sea otter wearing a beret",
        n=2,
        size="1024x1024"
    )
    assert edit

# MODERATION TESTS
@pytest.mark.parametrize("api_type", ["openai"])
def test_client_moderation(client):
    mod = client.moderation(
        input="hello world",
        model="text-moderation-latest"
    )
    assert mod

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", ["openai"])
async def test_client_amoderation(client):
    mod = await client.amoderation(
        input="hello world",
        model="text-moderation-latest"
    )
    assert mod

# AUDIO TRANSCRIBE TESTS
@pytest.mark.parametrize("api_type", ["openai"])
def test_client_transcribe_audio(client):
    file = open(AUDIO_FILE_PATH, "rb")
    audio = client.transcribe_audio(
        file=file,
        model="whisper-1"
    )
    assert audio

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", ["openai"])
async def test_client_atranscribe_audio(client):
    file = open(AUDIO_FILE_PATH, "rb")
    audio = await client.atranscribe_audio(
        file=file,
        model="whisper-1"
    )
    assert audio

# AUDIO TRANSLATE TESTS
@pytest.mark.parametrize("api_type", ["openai"])
def test_client_translate_audio(client):
    file = open(AUDIO_FILE_PATH, "rb")
    audio = client.translate_audio(
        file=file,
        model="whisper-1"
    )
    assert audio

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", ["openai"])
async def test_client_atranslate_audio(client):
    file = open(AUDIO_FILE_PATH, "rb")
    audio = await client.atranslate_audio(
        file=file,
        model="whisper-1"
    )
    assert audio
