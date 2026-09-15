from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class TypesProxy(LazyProxy[Any]):
    """A proxy for the `openai.types` module.

    This is used so that we can lazily import `openai.types` only when
    needed *and* so that users can just import `openai` and reference `openai.types`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("openai.types")
        return mod


types = TypesProxy().__as_proxied__()
