# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .alerts import (
        Alerts as Alerts,
        AsyncAlerts as AsyncAlerts,
        AlertsWithRawResponse as AlertsWithRawResponse,
        AsyncAlertsWithRawResponse as AsyncAlertsWithRawResponse,
        AlertsWithStreamingResponse as AlertsWithStreamingResponse,
        AsyncAlertsWithStreamingResponse as AsyncAlertsWithStreamingResponse,
    )
    from .safety import (
        Safety as Safety,
        AsyncSafety as AsyncSafety,
        SafetyWithRawResponse as SafetyWithRawResponse,
        AsyncSafetyWithRawResponse as AsyncSafetyWithRawResponse,
        SafetyWithStreamingResponse as SafetyWithStreamingResponse,
        AsyncSafetyWithStreamingResponse as AsyncSafetyWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Alerts": (".alerts", "Alerts"),
        "AsyncAlerts": (".alerts", "AsyncAlerts"),
        "AlertsWithRawResponse": (".alerts", "AlertsWithRawResponse"),
        "AsyncAlertsWithRawResponse": (".alerts", "AsyncAlertsWithRawResponse"),
        "AlertsWithStreamingResponse": (".alerts", "AlertsWithStreamingResponse"),
        "AsyncAlertsWithStreamingResponse": (".alerts", "AsyncAlertsWithStreamingResponse"),
        "Safety": (".safety", "Safety"),
        "AsyncSafety": (".safety", "AsyncSafety"),
        "SafetyWithRawResponse": (".safety", "SafetyWithRawResponse"),
        "AsyncSafetyWithRawResponse": (".safety", "AsyncSafetyWithRawResponse"),
        "SafetyWithStreamingResponse": (".safety", "SafetyWithStreamingResponse"),
        "AsyncSafetyWithStreamingResponse": (".safety", "AsyncSafetyWithStreamingResponse"),
    }
    _SUBMODULES = {
        "alerts",
        "safety",
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
    "Alerts",
    "AsyncAlerts",
    "AlertsWithRawResponse",
    "AsyncAlertsWithRawResponse",
    "AlertsWithStreamingResponse",
    "AsyncAlertsWithStreamingResponse",
    "Safety",
    "AsyncSafety",
    "SafetyWithRawResponse",
    "AsyncSafetyWithRawResponse",
    "SafetyWithStreamingResponse",
    "AsyncSafetyWithStreamingResponse",
]
