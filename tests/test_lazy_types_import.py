from __future__ import annotations

import importlib
import sys
from types import ModuleType


def _openai_modules() -> dict[str, object]:
    return {name: mod for name, mod in sys.modules.items() if name == "openai" or name.startswith("openai.")}


def test_openai_types_are_lazy_imported() -> None:
    original_modules = _openai_modules()

    for name in original_modules:
        sys.modules.pop(name, None)

    try:
        openai = importlib.import_module("openai")

        assert "openai.types" not in sys.modules

        # Attribute access should trigger the lazy import.
        assert openai.types.ChatModel is not None
        assert "openai.types" in sys.modules

        types_module = sys.modules["openai.types"]
        assert isinstance(openai.types, ModuleType)
        assert openai.types is types_module

        # Module reload should keep the binding pointed at the module object.
        reloaded = importlib.reload(openai.types)
        assert reloaded is openai.types
        assert reloaded is sys.modules["openai.types"]
    finally:
        for name in list(sys.modules):
            if name == "openai" or name.startswith("openai."):
                sys.modules.pop(name, None)
        sys.modules.update(original_modules)
