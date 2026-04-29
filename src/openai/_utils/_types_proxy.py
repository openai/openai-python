from __future__ import annotations

from types import ModuleType
from typing_extensions import override

from ._proxy import LazyProxy


class TypesProxy(LazyProxy[ModuleType]):
    """A proxy for the `openai.types` module.

    This lets `import openai` expose `openai.types` without importing all generated
    type modules until users actually access them.
    """

    @override
    def __load__(self) -> ModuleType:
        import importlib

        return importlib.import_module("openai.types")


types = TypesProxy().__as_proxied__()
