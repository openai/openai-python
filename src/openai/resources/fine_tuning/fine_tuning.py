# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from .jobs import Jobs, AsyncJobs, JobsWithRawResponse, AsyncJobsWithRawResponse
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["FineTuning", "AsyncFineTuning"]


class FineTuning(SyncAPIResource):
    @cached_property
    def jobs(self) -> Jobs:
        return Jobs(self._client)

    @cached_property
    def with_raw_response(self) -> FineTuningWithRawResponse:
        return FineTuningWithRawResponse(self)


class AsyncFineTuning(AsyncAPIResource):
    @cached_property
    def jobs(self) -> AsyncJobs:
        return AsyncJobs(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncFineTuningWithRawResponse:
        return AsyncFineTuningWithRawResponse(self)


class FineTuningWithRawResponse:
    def __init__(self, fine_tuning: FineTuning) -> None:
        self.jobs = JobsWithRawResponse(fine_tuning.jobs)


class AsyncFineTuningWithRawResponse:
    def __init__(self, fine_tuning: AsyncFineTuning) -> None:
        self.jobs = AsyncJobsWithRawResponse(fine_tuning.jobs)
