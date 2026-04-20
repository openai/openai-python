from __future__ import annotations

import sys
import importlib
from types import ModuleType


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

_LAZY_EXPORT_MODULES = (
    "openai.lib.azure",
    "openai.lib.streaming",
    "openai.lib._tools",
)


def _resolve_lazy_exports(openai_module: object) -> None:
    for name in _LAZY_EXPORT_NAMES:
        getattr(openai_module, name)


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

        for mod_name in _LAZY_EXPORT_MODULES:
            assert mod_name not in sys.modules

        _resolve_lazy_exports(openai)

        for mod_name in _LAZY_EXPORT_MODULES:
            assert mod_name in sys.modules
        for attr_name in _LAZY_EXPORT_NAMES:
            assert attr_name in openai.__dict__
    finally:
        _restore_openai_modules(original_modules)
