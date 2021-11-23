import pytest

from openai import Completion
from openai import Engine
from openai.util import ApiType

@pytest.mark.url
def test_completions_url_composition_azure() -> None:
    url = Completion.class_url("test_engine", "azure")
    assert url == '/openai/deployments/test_engine/completions?api-version=2021-11-01-preview'

@pytest.mark.url
def test_completions_url_composition_default() -> None:
    url = Completion.class_url("test_engine")
    assert url == '/v1/engines/test_engine/completions'

@pytest.mark.url
def test_completions_url_composition_open_ai() -> None:
    url = Completion.class_url("test_engine", "open_ai")
    assert url == '/v1/engines/test_engine/completions'

@pytest.mark.url
def test_completions_url_composition_invalid_type() -> None:
    with pytest.raises(Exception):
        url = Completion.class_url("test_engine", "invalid")

@pytest.mark.url
def test_completions_url_composition_instance_url_azure() -> None:
    completion = Completion(id="test_id", engine="test_engine", api_type="azure")
    url = completion.instance_url()
    assert url == "/openai/deployments/test_engine/completions/test_id?api-version=2021-11-01-preview"

@pytest.mark.url
def test_completions_url_composition_instance_url_default() -> None:
    completion = Completion(id="test_id", engine="test_engine")
    url = completion.instance_url()
    assert url == "/v1/engines/test_engine/completions/test_id"

@pytest.mark.url
def test_completions_url_composition_instance_url_open_ai() -> None:
    completion = Completion(id="test_id", engine="test_engine", api_type="open_ai")
    url = completion.instance_url()
    assert url == "/v1/engines/test_engine/completions/test_id"

@pytest.mark.url
def test_completions_url_composition_instance_url_invalid() -> None:
    completion = Completion(id="test_id", engine="test_engine", api_type="invalid")
    with pytest.raises(Exception):
        url = completion.instance_url()

@pytest.mark.url
def test_completions_url_composition_instance_url_timeout_azure() -> None:
    completion = Completion(id="test_id", engine="test_engine", api_type="azure")
    completion["timeout"] = 12
    url = completion.instance_url()
    assert url == "/openai/deployments/test_engine/completions/test_id?api-version=2021-11-01-preview&timeout=12"

@pytest.mark.url
def test_completions_url_composition_instance_url_timeout_openai() -> None:
    completion = Completion(id="test_id", engine="test_engine", api_type="open_ai" )
    completion["timeout"] = 12
    url = completion.instance_url()
    assert url == "/v1/engines/test_engine/completions/test_id?timeout=12"


@pytest.mark.url
def test_engine_search_url_composition_azure() -> None:
    engine = Engine(id="test_id", api_type="azure")
    assert engine.api_type == "azure"
    assert engine.typed_api_type == ApiType.AZURE
    url = engine.instance_url("test_operation")
    assert url == '/openai/deployments/test_id/test_operation?api-version=2021-11-01-preview'

@pytest.mark.url
def test_engine_search_url_composition_azure_no_operation() -> None:
    engine = Engine(id="test_id", api_type="azure")
    assert engine.api_type == "azure"
    assert engine.typed_api_type == ApiType.AZURE
    with pytest.raises(Exception):
        url = engine.instance_url()    

@pytest.mark.url
def test_engine_search_url_composition_default() -> None:
    engine = Engine(id="test_id")
    assert engine.api_type == None
    assert engine.typed_api_type == ApiType.OPEN_AI
    url = engine.instance_url()
    assert url == '/v1/engines/test_id'

@pytest.mark.url
def test_engine_search_url_composition_open_ai() -> None:
    engine = Engine(id="test_id", api_type="open_ai")
    assert engine.api_type == "open_ai"
    assert engine.typed_api_type == ApiType.OPEN_AI
    url = engine.instance_url()
    assert url == '/v1/engines/test_id'

@pytest.mark.url
def test_engine_search_url_composition_invalid_type() -> None:
    engine = Engine(id="test_id", api_type="invalid")
    assert engine.api_type == "invalid"
    with pytest.raises(Exception):
        assert engine.typed_api_type == ApiType.OPEN_AI

@pytest.mark.url
def test_engine_search_url_composition_invalid_search() -> None:
    engine = Engine(id="test_id", api_type="invalid")
    assert engine.api_type == "invalid"
    with pytest.raises(Exception):
        engine.search()
