from __future__ import annotations

import importlib
from typing import cast

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai._types import Headers


def test_header_omission_resolves_original_client_module_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    client_module = importlib.import_module("openai._client")

    class ReplacementOmit:
        pass

    monkeypatch.setattr(client_module, "Omit", ReplacementOmit)
    headers = cast(Headers, {"AUTHORIZATION": ReplacementOmit()})
    assert client_module._has_omitted_header(headers, "authorization")
    assert not client_module._has_omitted_header(headers, "api-key")
    assert not client_module._has_omitted_header({"Authorization": "bearer synthetic"}, "authorization")


@pytest.mark.anyio
@pytest.mark.parametrize("class_name", ["OpenAI", "AsyncOpenAI"])
async def test_saved_client_class_retains_lexical_super_after_module_rebinding(
    monkeypatch: pytest.MonkeyPatch, class_name: str
) -> None:
    client_module = importlib.import_module("openai._client")
    saved_class = OpenAI if class_name == "OpenAI" else AsyncOpenAI
    monkeypatch.setattr(client_module, class_name, object)
    if saved_class is OpenAI:
        with OpenAI(api_key="synthetic-key", http_client=httpx2.Client(trust_env=False)) as client:
            assert client.api_key == "synthetic-key"
    else:
        async_client = AsyncOpenAI(api_key="synthetic-key", http_client=httpx2.AsyncClient(trust_env=False))
        try:
            assert async_client.api_key == "synthetic-key"
        finally:
            await async_client.close()
