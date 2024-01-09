# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .completions import Completions, AsyncCompletions, CompletionsWithRawResponse, AsyncCompletionsWithRawResponse

__all__ = ["Chat", "AsyncChat"]


class Chat(SyncAPIResource):
    @cached_property
    def completions(self) -> Completions:
        return Completions(self._client)

    @cached_property
    def with_raw_response(self) -> ChatWithRawResponse:
        return ChatWithRawResponse(self)


class AsyncChat(AsyncAPIResource):
    @cached_property
    def completions(self) -> AsyncCompletions:
        return AsyncCompletions(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncChatWithRawResponse:
        return AsyncChatWithRawResponse(self)


class ChatWithRawResponse:
    def __init__(self, chat: Chat) -> None:
        self.completions = CompletionsWithRawResponse(chat.completions)


class AsyncChatWithRawResponse:
    def __init__(self, chat: AsyncChat) -> None:
        self.completions = AsyncCompletionsWithRawResponse(chat.completions)
