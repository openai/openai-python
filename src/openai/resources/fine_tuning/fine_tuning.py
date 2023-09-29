# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING

from .jobs import Jobs, AsyncJobs
from ..._resource import SyncAPIResource, AsyncAPIResource

if TYPE_CHECKING:
    from ..._client import OpenAI, AsyncOpenAI

__all__ = ["FineTuning", "AsyncFineTuning"]


class FineTuning(SyncAPIResource):
    jobs: Jobs

    def __init__(self, client: OpenAI) -> None:
        super().__init__(client)
        self.jobs = Jobs(client)


class AsyncFineTuning(AsyncAPIResource):
    jobs: AsyncJobs

    def __init__(self, client: AsyncOpenAI) -> None:
        super().__init__(client)
        self.jobs = AsyncJobs(client)
