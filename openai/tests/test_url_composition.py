import pytest

from openai import Completion

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
