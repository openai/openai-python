# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from .threads import Threads, AsyncThreads, ThreadsWithRawResponse, AsyncThreadsWithRawResponse
from ..._compat import cached_property
from .assistants import Assistants, AsyncAssistants, AssistantsWithRawResponse, AsyncAssistantsWithRawResponse
from ..._resource import SyncAPIResource, AsyncAPIResource
from .threads.threads import Threads, AsyncThreads
from .assistants.assistants import Assistants, AsyncAssistants

__all__ = ["Beta", "AsyncBeta"]


class Beta(SyncAPIResource):
    @cached_property
    def assistants(self) -> Assistants:
        return Assistants(self._client)

    @cached_property
    def threads(self) -> Threads:
        return Threads(self._client)

    @cached_property
    def with_raw_response(self) -> BetaWithRawResponse:
        return BetaWithRawResponse(self)


class AsyncBeta(AsyncAPIResource):
    @cached_property
    def assistants(self) -> AsyncAssistants:
        return AsyncAssistants(self._client)

    @cached_property
    def threads(self) -> AsyncThreads:
        return AsyncThreads(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncBetaWithRawResponse:
        return AsyncBetaWithRawResponse(self)


class BetaWithRawResponse:
    def __init__(self, beta: Beta) -> None:
        self.assistants = AssistantsWithRawResponse(beta.assistants)
        self.threads = ThreadsWithRawResponse(beta.threads)


class AsyncBetaWithRawResponse:
    def __init__(self, beta: AsyncBeta) -> None:
        self.assistants = AsyncAssistantsWithRawResponse(beta.assistants)
        self.threads = AsyncThreadsWithRawResponse(beta.threads)
