# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["InviteDeleteResponse"]


class InviteDeleteResponse(BaseModel):
    id: str

    deleted: bool

    object: Literal["organization.invite.deleted"]
    """The object type, which is always `organization.invite.deleted`"""
