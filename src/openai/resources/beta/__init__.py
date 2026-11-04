# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .beta import (
        Beta as Beta,
        AsyncBeta as AsyncBeta,
        BetaWithRawResponse as BetaWithRawResponse,
        AsyncBetaWithRawResponse as AsyncBetaWithRawResponse,
        BetaWithStreamingResponse as BetaWithStreamingResponse,
        AsyncBetaWithStreamingResponse as AsyncBetaWithStreamingResponse,
    )
    from .agents import (
        Agents as Agents,
        AsyncAgents as AsyncAgents,
        AgentsWithRawResponse as AgentsWithRawResponse,
        AsyncAgentsWithRawResponse as AsyncAgentsWithRawResponse,
        AgentsWithStreamingResponse as AgentsWithStreamingResponse,
        AsyncAgentsWithStreamingResponse as AsyncAgentsWithStreamingResponse,
    )
    from .chatkit import (
        ChatKit as ChatKit,
        AsyncChatKit as AsyncChatKit,
        ChatKitWithRawResponse as ChatKitWithRawResponse,
        AsyncChatKitWithRawResponse as AsyncChatKitWithRawResponse,
        ChatKitWithStreamingResponse as ChatKitWithStreamingResponse,
        AsyncChatKitWithStreamingResponse as AsyncChatKitWithStreamingResponse,
    )
    from .threads import (
        Threads as Threads,
        AsyncThreads as AsyncThreads,
        ThreadsWithRawResponse as ThreadsWithRawResponse,
        AsyncThreadsWithRawResponse as AsyncThreadsWithRawResponse,
        ThreadsWithStreamingResponse as ThreadsWithStreamingResponse,
        AsyncThreadsWithStreamingResponse as AsyncThreadsWithStreamingResponse,
    )
    from .responses import (
        Responses as Responses,
        AsyncResponses as AsyncResponses,
        ResponsesWithRawResponse as ResponsesWithRawResponse,
        AsyncResponsesWithRawResponse as AsyncResponsesWithRawResponse,
        ResponsesWithStreamingResponse as ResponsesWithStreamingResponse,
        AsyncResponsesWithStreamingResponse as AsyncResponsesWithStreamingResponse,
    )
    from .assistants import (
        Assistants as Assistants,
        AsyncAssistants as AsyncAssistants,
        AssistantsWithRawResponse as AssistantsWithRawResponse,
        AsyncAssistantsWithRawResponse as AsyncAssistantsWithRawResponse,
        AssistantsWithStreamingResponse as AssistantsWithStreamingResponse,
        AsyncAssistantsWithStreamingResponse as AsyncAssistantsWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Agents": (".agents", "Agents"),
        "AsyncAgents": (".agents", "AsyncAgents"),
        "AgentsWithRawResponse": (".agents", "AgentsWithRawResponse"),
        "AsyncAgentsWithRawResponse": (".agents", "AsyncAgentsWithRawResponse"),
        "AgentsWithStreamingResponse": (".agents", "AgentsWithStreamingResponse"),
        "AsyncAgentsWithStreamingResponse": (".agents", "AsyncAgentsWithStreamingResponse"),
        "Responses": (".responses", "Responses"),
        "AsyncResponses": (".responses", "AsyncResponses"),
        "ResponsesWithRawResponse": (".responses", "ResponsesWithRawResponse"),
        "AsyncResponsesWithRawResponse": (".responses", "AsyncResponsesWithRawResponse"),
        "ResponsesWithStreamingResponse": (".responses", "ResponsesWithStreamingResponse"),
        "AsyncResponsesWithStreamingResponse": (".responses", "AsyncResponsesWithStreamingResponse"),
        "ChatKit": (".chatkit", "ChatKit"),
        "AsyncChatKit": (".chatkit", "AsyncChatKit"),
        "ChatKitWithRawResponse": (".chatkit", "ChatKitWithRawResponse"),
        "AsyncChatKitWithRawResponse": (".chatkit", "AsyncChatKitWithRawResponse"),
        "ChatKitWithStreamingResponse": (".chatkit", "ChatKitWithStreamingResponse"),
        "AsyncChatKitWithStreamingResponse": (".chatkit", "AsyncChatKitWithStreamingResponse"),
        "Assistants": (".assistants", "Assistants"),
        "AsyncAssistants": (".assistants", "AsyncAssistants"),
        "AssistantsWithRawResponse": (".assistants", "AssistantsWithRawResponse"),
        "AsyncAssistantsWithRawResponse": (".assistants", "AsyncAssistantsWithRawResponse"),
        "AssistantsWithStreamingResponse": (".assistants", "AssistantsWithStreamingResponse"),
        "AsyncAssistantsWithStreamingResponse": (".assistants", "AsyncAssistantsWithStreamingResponse"),
        "Threads": (".threads", "Threads"),
        "AsyncThreads": (".threads", "AsyncThreads"),
        "ThreadsWithRawResponse": (".threads", "ThreadsWithRawResponse"),
        "AsyncThreadsWithRawResponse": (".threads", "AsyncThreadsWithRawResponse"),
        "ThreadsWithStreamingResponse": (".threads", "ThreadsWithStreamingResponse"),
        "AsyncThreadsWithStreamingResponse": (".threads", "AsyncThreadsWithStreamingResponse"),
        "Beta": (".beta", "Beta"),
        "AsyncBeta": (".beta", "AsyncBeta"),
        "BetaWithRawResponse": (".beta", "BetaWithRawResponse"),
        "AsyncBetaWithRawResponse": (".beta", "AsyncBetaWithRawResponse"),
        "BetaWithStreamingResponse": (".beta", "BetaWithStreamingResponse"),
        "AsyncBetaWithStreamingResponse": (".beta", "AsyncBetaWithStreamingResponse"),
    }
    _SUBMODULES = {
        "agents",
        "assistants",
        "beta",
        "chatkit",
        "responses",
        "threads",
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
    "Agents",
    "AsyncAgents",
    "AgentsWithRawResponse",
    "AsyncAgentsWithRawResponse",
    "AgentsWithStreamingResponse",
    "AsyncAgentsWithStreamingResponse",
    "Responses",
    "AsyncResponses",
    "ResponsesWithRawResponse",
    "AsyncResponsesWithRawResponse",
    "ResponsesWithStreamingResponse",
    "AsyncResponsesWithStreamingResponse",
    "ChatKit",
    "AsyncChatKit",
    "ChatKitWithRawResponse",
    "AsyncChatKitWithRawResponse",
    "ChatKitWithStreamingResponse",
    "AsyncChatKitWithStreamingResponse",
    "Assistants",
    "AsyncAssistants",
    "AssistantsWithRawResponse",
    "AsyncAssistantsWithRawResponse",
    "AssistantsWithStreamingResponse",
    "AsyncAssistantsWithStreamingResponse",
    "Threads",
    "AsyncThreads",
    "ThreadsWithRawResponse",
    "AsyncThreadsWithRawResponse",
    "ThreadsWithStreamingResponse",
    "AsyncThreadsWithStreamingResponse",
    "Beta",
    "AsyncBeta",
    "BetaWithRawResponse",
    "AsyncBetaWithRawResponse",
    "BetaWithStreamingResponse",
    "AsyncBetaWithStreamingResponse",
]
