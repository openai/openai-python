# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .realtime_response_create_params_param import RealtimeResponseCreateParamsParam

__all__ = ["ResponseCreateEventParam"]


class ResponseCreateEventParam(TypedDict, total=False):
    type: Required[Literal["response.create"]]
    """The event type, must be `response.create`."""

    event_id: str
    """Optional client-generated ID used to identify this event."""

    response: RealtimeResponseCreateParamsParam
    """Create a new Realtime response with these parameters"""
