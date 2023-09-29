# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING

from ..._resource import SyncAPIResource, AsyncAPIResource
from .completions import Completions, AsyncCompletions

if TYPE_CHECKING:
    from ..._client import OpenAI, AsyncOpenAI

__all__ = ["Chat", "AsyncChat"]


class Chat(SyncAPIResource):
    completions: Completions

    def __init__(self, client: OpenAI) -> None:
        super().__init__(client)
        self.completions = Completions(client)


class AsyncChat(AsyncAPIResource):
    completions: AsyncCompletions

    def __init__(self, client: AsyncOpenAI) -> None:
        super().__init__(client)
        self.completions = AsyncCompletions(client)
