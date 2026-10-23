# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .automations import (
        Automations as Automations,
        AsyncAutomations as AsyncAutomations,
        AutomationsWithRawResponse as AutomationsWithRawResponse,
        AsyncAutomationsWithRawResponse as AsyncAutomationsWithRawResponse,
        AutomationsWithStreamingResponse as AutomationsWithStreamingResponse,
        AsyncAutomationsWithStreamingResponse as AsyncAutomationsWithStreamingResponse,
    )
    from .invocations import (
        Invocations as Invocations,
        AsyncInvocations as AsyncInvocations,
        InvocationsWithRawResponse as InvocationsWithRawResponse,
        AsyncInvocationsWithRawResponse as AsyncInvocationsWithRawResponse,
        InvocationsWithStreamingResponse as InvocationsWithStreamingResponse,
        AsyncInvocationsWithStreamingResponse as AsyncInvocationsWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Invocations": (".invocations", "Invocations"),
        "AsyncInvocations": (".invocations", "AsyncInvocations"),
        "InvocationsWithRawResponse": (".invocations", "InvocationsWithRawResponse"),
        "AsyncInvocationsWithRawResponse": (".invocations", "AsyncInvocationsWithRawResponse"),
        "InvocationsWithStreamingResponse": (".invocations", "InvocationsWithStreamingResponse"),
        "AsyncInvocationsWithStreamingResponse": (".invocations", "AsyncInvocationsWithStreamingResponse"),
        "Automations": (".automations", "Automations"),
        "AsyncAutomations": (".automations", "AsyncAutomations"),
        "AutomationsWithRawResponse": (".automations", "AutomationsWithRawResponse"),
        "AsyncAutomationsWithRawResponse": (".automations", "AsyncAutomationsWithRawResponse"),
        "AutomationsWithStreamingResponse": (".automations", "AutomationsWithStreamingResponse"),
        "AsyncAutomationsWithStreamingResponse": (".automations", "AsyncAutomationsWithStreamingResponse"),
    }
    _SUBMODULES = {
        "automations",
        "invocations",
    }

    def __getattr__(name: str) -> _t.Any:
        import importlib

        if name in _EXPORTS:
            module_name, symbol_name = _EXPORTS[name]
            value = getattr(importlib.import_module(module_name, __name__), symbol_name)
        elif name in _SUBMODULES:
            value = importlib.import_module(f".{name}", __name__)
        else:
            raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
        globals()[name] = value
        return value

    def __dir__() -> list[str]:
        return sorted(set(globals()) | set(_EXPORTS) | _SUBMODULES)


__all__ = [
    "Invocations",
    "AsyncInvocations",
    "InvocationsWithRawResponse",
    "AsyncInvocationsWithRawResponse",
    "InvocationsWithStreamingResponse",
    "AsyncInvocationsWithStreamingResponse",
    "Automations",
    "AsyncAutomations",
    "AutomationsWithRawResponse",
    "AsyncAutomationsWithRawResponse",
    "AutomationsWithStreamingResponse",
    "AsyncAutomationsWithStreamingResponse",
]
