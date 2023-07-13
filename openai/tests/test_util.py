import json
from pathlib import Path

import pytest
from pytest import MonkeyPatch

from openai import util


@pytest.fixture(scope="function")
def api_key_file(tmp_path: Path, monkeypatch: MonkeyPatch) -> Path:
    key_file = tmp_path / "openai_api_key"
    monkeypatch.setattr("openai.api_key_path", str(key_file))
    return key_file


def test_openai_api_key_path(api_key_file: Path) -> None:
    api_key_file.write_text("sk-foo\n", encoding="utf-8")
    assert util.default_api_key() == "sk-foo"


def test_openai_api_key_path_with_malformed_key(api_key_file: Path) -> None:
    api_key_file.write_text("malformed-api-key\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed API key"):
        util.default_api_key()


def test_key_order_openai_object_rendering() -> None:
    sample_response = {
        "id": "chatcmpl-7NaPEA6sgX7LnNPyKPbRlsyqLbr5V",
        "object": "chat.completion",
        "created": 1685855844,
        "model": "gpt-3.5-turbo-0301",
        "usage": {"prompt_tokens": 57, "completion_tokens": 40, "total_tokens": 97},
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "The 2020 World Series was played at Globe Life Field in Arlington, Texas. It was the first time that the World Series was played at a neutral site because of the COVID-19 pandemic.",
                },
                "finish_reason": "stop",
                "index": 0,
            }
        ],
    }

    oai_object = util.convert_to_openai_object(sample_response)
    # The `__str__` method was sorting while dumping to json
    assert list(json.loads(str(oai_object)).keys()) == list(sample_response.keys())
