# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

from .beta_response_input_item_param import BetaResponseInputItemParam

__all__ = ["BetaResponseInjectEventParam"]


class BetaResponseInjectEventParam(TypedDict, total=False):
    """
    Injects input items into an active response over a WebSocket connection.
    The items are validated and committed atomically. Currently, the server
    accepts client-owned tool outputs that resume a waiting agent.
    """

    input: Required[Iterable[BetaResponseInputItemParam]]
    """Input items to inject into the active response."""

    response_id: Required[str]
    """The ID of the active response that should receive the input."""

    type: Required[Literal["response.inject"]]
    """The event discriminator. Always `response.inject`."""
