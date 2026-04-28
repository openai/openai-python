from __future__ import annotations

import os
import sys
import importlib
from types import ModuleType

import pytest


def _openai_modules() -> dict[str, ModuleType]:
    return {name: mod for name, mod in sys.modules.items() if name == "openai" or name.startswith("openai.")}


def _restore_openai_modules(original_modules: dict[str, ModuleType]) -> None:
    for name in list(sys.modules):
        if name == "openai" or name.startswith("openai."):
            sys.modules.pop(name, None)
    sys.modules.update(original_modules)


_LAZY_EXPORT_NAMES = (
    "AzureOpenAI",
    "AsyncAzureOpenAI",
    "pydantic_function_tool",
    "AssistantEventHandler",
    "AsyncAssistantEventHandler",
)


def _resolve_lazy_exports(openai_module: object) -> None:
    for name in _LAZY_EXPORT_NAMES:
        getattr(openai_module, name)


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

        assert "openai.lib.azure" in sys.modules
        assert "AzureOpenAI" in openai.__dict__

        client = openai.OpenAI(timeout=20.0)
        page = client.models.list()
        assert page.data is not None
    finally:
        if client is not None:
            client.close()
        _restore_openai_modules(original_modules)
