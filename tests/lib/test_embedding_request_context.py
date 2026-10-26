from __future__ import annotations

from typing import cast

import pytest

from openai._types import Omit, NotGiven, omit, not_given
from openai.lib._parsing import _embeddings as embeddings_parser
from tests.lib.test_embeddings import VALUES, ENCODED, make_response
from openai.types.create_embedding_response import CreateEmbeddingResponse


@pytest.mark.parametrize(
    ("encoding_format", "decode"),
    [(omit, True), (not_given, True), ("float", False), ("base64", False)],
    ids=["omit", "not-given", "float", "base64"],
)
def test_preparation_retains_original_encoding_for_lazy_response_parsing(
    encoding_format: str | Omit | NotGiven,
    decode: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    checks: list[None] = []

    def has_numpy() -> bool:
        checks.append(None)
        return False

    monkeypatch.setattr(embeddings_parser, "has_numpy", has_numpy)
    body: dict[str, object] = {
        "input": "hello",
        "model": "text-embedding-3-small",
        "encoding_format": encoding_format,
        "future_option": {"enabled": True},
    }
    original = body.copy()
    context = embeddings_parser.prepare_embedding_request(object(), body, encoding_format=encoding_format)
    prepared = cast(dict[str, object], context.body)

    assert body == original
    assert prepared is not body
    assert prepared["encoding_format"] == ("base64" if decode else encoding_format)
    assert prepared["future_option"] is body["future_option"]
    assert checks == []

    response = make_response(ENCODED)
    parsed = cast(CreateEmbeddingResponse, context.post_parser(response))
    assert parsed is response
    assert parsed.data[0].embedding == (VALUES if decode else ENCODED)
    assert len(checks) == (1 if decode else 0)
