from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._utils import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `openai.resources` module.

    This is used so that we can lazily import `openai.resources` only when
    needed *and* so that users can just import `openai` and reference `openai.resources`

    e.g.

    ```py
    import openai

    completions: openai.resources.chat.Completions
    ```
    """

    _loaded = None

    @override
    def __load__(self) -> Any:
        if self._loaded is not None:
            return self._loaded

        import importlib

        self._loaded = mod = importlib.import_module("openai.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
