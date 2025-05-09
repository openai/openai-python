from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._utils import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    _loaded = None

    @override
    def __load__(self) -> Any:
        if self._loaded is not None:
            return self._loaded

        import importlib
        mod = importlib.import_module('openai.resources')
        self._loaded = mod
        return mod


resources = ResourcesProxy().__as_proxied__()
