from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class TypesProxy(LazyProxy[Any]):
    """Lazily import ``openai.types`` when an exported type is accessed."""

    @override
    def __load__(self) -> Any:
        import importlib

        return importlib.import_module("openai.types")


types = TypesProxy().__as_proxied__()
