# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["AgentBrowserAuthenticationSubmitParam", "Field"]


class Field(TypedDict, total=False):
    """One user-entered value, including non-password fields such as an email address."""

    field_id: Required[str]
    """The field ID from the required action."""

    value: Required[str]
    """The value to enter into the registered control."""


class AgentBrowserAuthenticationSubmitParam(TypedDict, total=False):
    action: Required[Literal["submit"]]

    fields: Required[Iterable[Field]]
    """Values for up to six active fields in the required action.

    The submitted field-value mapping and selected option must fit within 120 KiB of
    JSON.
    """

    type: Required[Literal["browser_authentication"]]

    selected_option: Optional[str]
    """The chosen method. Required when the required action contains options."""
