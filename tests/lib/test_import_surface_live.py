from __future__ import annotations

import os
import sys
import importlib

import pytest


def _openai_modules() -> dict[str, object]:
    return {name: mod for name, mod in sys.modules.items() if name == "openai" or name.startswith("openai.")}


def _restore_openai_modules(original_modules: dict[str, object]) -> None:
    for name in list(sys.modules):
        if name == "openai" or name.startswith("openai."):
            sys.modules.pop(name, None)
    sys.modules.update(original_modules)


def _resolve_lazy_exports(openai_module: object) -> None:
    getattr(openai_module, "types")
    getattr(openai_module, "AzureOpenAI")
    getattr(openai_module, "AsyncAzureOpenAI")
    getattr(openai_module, "pydantic_function_tool")
    getattr(openai_module, "AssistantEventHandler")
    getattr(openai_module, "AsyncAssistantEventHandler")


@pytest.mark.skipif(os.environ.get("OPENAI_LIVE") != "1", reason="requires OPENAI_LIVE=1")
@pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="requires OPENAI_API_KEY")
def test_explicit_lazy_export_resolution_allows_real_request() -> None:
    original_modules = _openai_modules()

    for name in original_modules:
        sys.modules.pop(name, None)

    client = None
    try:
        openai = importlib.import_module("openai")

        _resolve_lazy_exports(openai)

        assert "openai.types" in sys.modules
        assert "openai.lib.azure" in sys.modules
        assert "AzureOpenAI" in openai.__dict__

        client = openai.OpenAI(timeout=20.0)
        page = client.models.list()
        assert page.data is not None
    finally:
        if client is not None:
            client.close()
        _restore_openai_modules(original_modules)
