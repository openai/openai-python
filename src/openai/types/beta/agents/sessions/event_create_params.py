# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo
from ...agent_session_input_param import AgentSessionInputParam

__all__ = ["EventCreateParams"]


class EventCreateParams(TypedDict, total=False):
    events: Required[Iterable[AgentSessionInputParam]]
    """The input events to submit to the session."""

    idempotency_key: Annotated[str, PropertyInfo(alias="Idempotency-Key")]
