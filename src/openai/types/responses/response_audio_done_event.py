# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseAudioDoneEvent"]


class ResponseAudioDoneEvent(BaseModel):
    type: Literal["response.audio.done"]
    """The type of the event. Always `response.audio.done`."""
