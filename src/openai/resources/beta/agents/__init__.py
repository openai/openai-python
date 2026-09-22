# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .agents import (
        Agents as Agents,
        AsyncAgents as AsyncAgents,
        AgentsWithRawResponse as AgentsWithRawResponse,
        AsyncAgentsWithRawResponse as AsyncAgentsWithRawResponse,
        AgentsWithStreamingResponse as AgentsWithStreamingResponse,
        AsyncAgentsWithStreamingResponse as AsyncAgentsWithStreamingResponse,
    )
    from .vaults import (
        Vaults as Vaults,
        AsyncVaults as AsyncVaults,
        VaultsWithRawResponse as VaultsWithRawResponse,
        AsyncVaultsWithRawResponse as AsyncVaultsWithRawResponse,
        VaultsWithStreamingResponse as VaultsWithStreamingResponse,
        AsyncVaultsWithStreamingResponse as AsyncVaultsWithStreamingResponse,
    )
    from .sessions import (
        Sessions as Sessions,
        AsyncSessions as AsyncSessions,
        SessionsWithRawResponse as SessionsWithRawResponse,
        AsyncSessionsWithRawResponse as AsyncSessionsWithRawResponse,
        SessionsWithStreamingResponse as SessionsWithStreamingResponse,
        AsyncSessionsWithStreamingResponse as AsyncSessionsWithStreamingResponse,
    )
    from .environments import (
        Environments as Environments,
        AsyncEnvironments as AsyncEnvironments,
        EnvironmentsWithRawResponse as EnvironmentsWithRawResponse,
        AsyncEnvironmentsWithRawResponse as AsyncEnvironmentsWithRawResponse,
        EnvironmentsWithStreamingResponse as EnvironmentsWithStreamingResponse,
        AsyncEnvironmentsWithStreamingResponse as AsyncEnvironmentsWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Environments": (".environments", "Environments"),
        "AsyncEnvironments": (".environments", "AsyncEnvironments"),
        "EnvironmentsWithRawResponse": (".environments", "EnvironmentsWithRawResponse"),
        "AsyncEnvironmentsWithRawResponse": (".environments", "AsyncEnvironmentsWithRawResponse"),
        "EnvironmentsWithStreamingResponse": (".environments", "EnvironmentsWithStreamingResponse"),
        "AsyncEnvironmentsWithStreamingResponse": (".environments", "AsyncEnvironmentsWithStreamingResponse"),
        "Vaults": (".vaults", "Vaults"),
        "AsyncVaults": (".vaults", "AsyncVaults"),
        "VaultsWithRawResponse": (".vaults", "VaultsWithRawResponse"),
        "AsyncVaultsWithRawResponse": (".vaults", "AsyncVaultsWithRawResponse"),
        "VaultsWithStreamingResponse": (".vaults", "VaultsWithStreamingResponse"),
        "AsyncVaultsWithStreamingResponse": (".vaults", "AsyncVaultsWithStreamingResponse"),
        "Sessions": (".sessions", "Sessions"),
        "AsyncSessions": (".sessions", "AsyncSessions"),
        "SessionsWithRawResponse": (".sessions", "SessionsWithRawResponse"),
        "AsyncSessionsWithRawResponse": (".sessions", "AsyncSessionsWithRawResponse"),
        "SessionsWithStreamingResponse": (".sessions", "SessionsWithStreamingResponse"),
        "AsyncSessionsWithStreamingResponse": (".sessions", "AsyncSessionsWithStreamingResponse"),
        "Agents": (".agents", "Agents"),
        "AsyncAgents": (".agents", "AsyncAgents"),
        "AgentsWithRawResponse": (".agents", "AgentsWithRawResponse"),
        "AsyncAgentsWithRawResponse": (".agents", "AsyncAgentsWithRawResponse"),
        "AgentsWithStreamingResponse": (".agents", "AgentsWithStreamingResponse"),
        "AsyncAgentsWithStreamingResponse": (".agents", "AsyncAgentsWithStreamingResponse"),
    }
    _SUBMODULES = {
        "agents",
        "environments",
        "sessions",
        "vaults",
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
    "Environments",
    "AsyncEnvironments",
    "EnvironmentsWithRawResponse",
    "AsyncEnvironmentsWithRawResponse",
    "EnvironmentsWithStreamingResponse",
    "AsyncEnvironmentsWithStreamingResponse",
    "Vaults",
    "AsyncVaults",
    "VaultsWithRawResponse",
    "AsyncVaultsWithRawResponse",
    "VaultsWithStreamingResponse",
    "AsyncVaultsWithStreamingResponse",
    "Sessions",
    "AsyncSessions",
    "SessionsWithRawResponse",
    "AsyncSessionsWithRawResponse",
    "SessionsWithStreamingResponse",
    "AsyncSessionsWithStreamingResponse",
    "Agents",
    "AsyncAgents",
    "AgentsWithRawResponse",
    "AsyncAgentsWithRawResponse",
    "AgentsWithStreamingResponse",
    "AsyncAgentsWithStreamingResponse",
]
