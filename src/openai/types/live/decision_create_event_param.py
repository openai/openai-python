# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["DecisionCreateEventParam"]


class DecisionCreateEventParam(TypedDict, total=False):
    """
    Evaluate the configured questions using the current conversation and Decision inputs. Reusing an event_id is rejected for the lifetime of the session.
    """

    event_id: Required[str]

    type: Required[Literal["decision.create"]]
