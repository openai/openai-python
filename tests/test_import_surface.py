from __future__ import annotations

import importlib
import sys


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


def test_openai_azure_is_lazy_imported() -> None:
    original_modules = _openai_modules()

    for name in original_modules:
        sys.modules.pop(name, None)

    try:
        openai = importlib.import_module("openai")

        assert "openai.lib.azure" not in sys.modules

        assert openai.AzureOpenAI is not None
        assert "openai.lib.azure" in sys.modules
    finally:
        _restore_openai_modules(original_modules)


def test_openai_can_explicitly_resolve_lazy_exports() -> None:
    original_modules = _openai_modules()

    for name in original_modules:
        sys.modules.pop(name, None)

    try:
        openai = importlib.import_module("openai")

        assert "openai.types" not in sys.modules
        assert "openai.lib.azure" not in sys.modules

        _resolve_lazy_exports(openai)

        assert "openai.types" in sys.modules
        assert "openai.lib.azure" in sys.modules
        assert "AzureOpenAI" in openai.__dict__
        assert "AsyncAzureOpenAI" in openai.__dict__
        assert "pydantic_function_tool" in openai.__dict__
        assert "AssistantEventHandler" in openai.__dict__
        assert "AsyncAssistantEventHandler" in openai.__dict__
    finally:
        _restore_openai_modules(original_modules)
