# File generated from our OpenAPI spec by Stainless.

from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["MessageCreationStepDetails", "MessageCreation"]


class MessageCreation(BaseModel):
    message_id: str
    """The ID of the Message that was created by this Run Step."""


class MessageCreationStepDetails(BaseModel):
    message_creation: MessageCreation

    type: Literal["message_creation"]
    """Will always be `message_creation``."""
