# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["OutputAudioBufferClearEventParam"]


class OutputAudioBufferClearEventParam(TypedDict, total=False):
    type: Required[Literal["output_audio_buffer.clear"]]
    """The event type, must be `output_audio_buffer.clear`."""

    event_id: str
    """The unique ID of the client event used for error handling."""
