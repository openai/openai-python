# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["InviteCreateParams", "Project"]


class InviteCreateParams(TypedDict, total=False):
    email: Required[str]
    """Send an email to this address"""

    role: Required[Literal["reader", "owner"]]
    """`owner` or `reader`"""

    projects: Iterable[Project]
    """
    An array of projects to which membership is granted at the same time the org
    invite is accepted. If omitted, the user will be invited to the default project
    for compatibility with legacy behavior.
    """


class Project(TypedDict, total=False):
    id: Required[str]
    """Project's public ID"""

    role: Required[Literal["member", "owner"]]
    """Project membership role"""
