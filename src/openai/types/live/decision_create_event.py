# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["DecisionCreateEvent"]


class DecisionCreateEvent(BaseModel):
    """
    Evaluate the configured questions using the current conversation and Decision inputs. Reusing an event_id is rejected for the lifetime of the session.
    """

    event_id: str

    type: Literal["decision.create"]
