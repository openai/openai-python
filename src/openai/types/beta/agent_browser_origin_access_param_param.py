# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["AgentBrowserOriginAccessParamParam"]


class AgentBrowserOriginAccessParamParam(TypedDict, total=False):
    decision: Required[Literal["approve", "deny", "cancel"]]
    """Whether to allow, deny, or cancel the requested origin access.

    - `approve` - Allow the browser to access this origin.
    - `deny` - Deny access to this origin.
    - `cancel` - Dismiss this request without approving access.
    """

    type: Required[Literal["browser_origin_access"]]
