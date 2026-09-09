# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from .alerts import (
    Alerts,
    AsyncAlerts,
    AlertsWithRawResponse,
    AsyncAlertsWithRawResponse,
    AlertsWithStreamingResponse,
    AsyncAlertsWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["Safety", "AsyncSafety"]


class Safety(SyncAPIResource):
    @cached_property
    def alerts(self) -> Alerts:
        return Alerts(self._client)

    @cached_property
    def with_raw_response(self) -> SafetyWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return SafetyWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SafetyWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return SafetyWithStreamingResponse(self)


class AsyncSafety(AsyncAPIResource):
    @cached_property
    def alerts(self) -> AsyncAlerts:
        return AsyncAlerts(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncSafetyWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSafetyWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSafetyWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncSafetyWithStreamingResponse(self)


class SafetyWithRawResponse:
    def __init__(self, safety: Safety) -> None:
        self._safety = safety

    @cached_property
    def alerts(self) -> AlertsWithRawResponse:
        return AlertsWithRawResponse(self._safety.alerts)


class AsyncSafetyWithRawResponse:
    def __init__(self, safety: AsyncSafety) -> None:
        self._safety = safety

    @cached_property
    def alerts(self) -> AsyncAlertsWithRawResponse:
        return AsyncAlertsWithRawResponse(self._safety.alerts)


class SafetyWithStreamingResponse:
    def __init__(self, safety: Safety) -> None:
        self._safety = safety

    @cached_property
    def alerts(self) -> AlertsWithStreamingResponse:
        return AlertsWithStreamingResponse(self._safety.alerts)


class AsyncSafetyWithStreamingResponse:
    def __init__(self, safety: AsyncSafety) -> None:
        self._safety = safety

    @cached_property
    def alerts(self) -> AsyncAlertsWithStreamingResponse:
        return AsyncAlertsWithStreamingResponse(self._safety.alerts)
