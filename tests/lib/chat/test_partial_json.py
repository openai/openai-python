from __future__ import annotations

import json
from typing import Any

import pytest
from jiter import from_json

from openai.lib.streaming._partial_json import PartialJSONParser


@pytest.mark.parametrize(
    "document",
    [
        json.dumps({"done": [1], "content": 'quote: " slash: \\ newline: \n emoji: 😀'}),
        json.dumps({"content": "café 漢字"}, ensure_ascii=False),
        '{"content": "\\q"}',
        '{"content": "\\uD800x"}',
    ],
)
def test_partial_json_matches_jiter(document: str) -> None:
    parser = PartialJSONParser()
    for end in range(1, len(document) + 1):
        value = document[:end]
        try:
            expected = from_json(value.encode("utf-8"), partial_mode=True)
        except (ValueError, UnicodeEncodeError) as exc:
            with pytest.raises(type(exc)) as actual:
                parser.parse(value)
            assert str(actual.value) == str(exc)
            # A failed stream ends here, as it does in the streaming helper.
            break
        else:
            assert parser.parse(value) == expected


def test_partial_json_does_not_share_mutable_values() -> None:
    parser = PartialJSONParser()
    prefix = '{"done": [1], "content": "'
    parsed = parser.parse(prefix)
    parsed["done"].append(2)
    assert parser.parse(prefix + "text") == {"done": [1]}


def test_partial_json_parses_fixed_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    from openai.lib.streaming import _partial_json

    lengths: list[int] = []

    def recording_parse(data: bytes, *, partial_mode: bool) -> Any:
        lengths.append(len(data))
        return from_json(data, partial_mode=partial_mode)

    monkeypatch.setattr(_partial_json, "from_json", recording_parse)
    parser = PartialJSONParser()
    prefix = '{"content": "'
    for size in range(0, 10000, 10):
        parser.parse(prefix + "a" * size)
    assert set(lengths) == {len(prefix)}
    assert parser.parse(prefix + "a" * 9990 + '"}') == {"content": "a" * 9990}
