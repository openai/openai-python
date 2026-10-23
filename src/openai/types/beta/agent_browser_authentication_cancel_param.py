# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["AgentBrowserAuthenticationCancelParam"]


class AgentBrowserAuthenticationCancelParam(TypedDict, total=False):
    action: Required[Literal["cancel"]]

    type: Required[Literal["browser_authentication"]]
