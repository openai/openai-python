import typing as _t

if _t.TYPE_CHECKING:
    from ._assistants import (
        AssistantEventHandler as AssistantEventHandler,
        AssistantEventHandlerT as AssistantEventHandlerT,
        AssistantStreamManager as AssistantStreamManager,
        AsyncAssistantEventHandler as AsyncAssistantEventHandler,
        AsyncAssistantEventHandlerT as AsyncAssistantEventHandlerT,
        AsyncAssistantStreamManager as AsyncAssistantStreamManager,
    )
else:

    def __getattr__(name: str) -> _t.Any:
        if name in __all__:
            from importlib import import_module

            value = getattr(import_module("._assistants", __name__), name)
            globals()[name] = value
            return value
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    def __dir__() -> list[str]:
        return sorted(set(globals()) | set(__all__))


__all__ = [
    "AssistantEventHandler",
    "AssistantEventHandlerT",
    "AssistantStreamManager",
    "AsyncAssistantEventHandler",
    "AsyncAssistantEventHandlerT",
    "AsyncAssistantStreamManager",
]
