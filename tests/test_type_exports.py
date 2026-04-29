from __future__ import annotations

import openai.types
import openai.types.chat
import openai.types.responses


def test_major_types_are_exported_from_types_package() -> None:
    assert openai.types.ChatCompletion is openai.types.chat.ChatCompletion
    assert openai.types.Response is openai.types.responses.Response
    assert openai.types.ResponseUsage is openai.types.responses.ResponseUsage
