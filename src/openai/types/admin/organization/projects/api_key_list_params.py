# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["APIKeyListParams"]


class APIKeyListParams(TypedDict, total=False):
    after: str
    """A cursor for use in pagination.

    `after` is an object ID that defines your place in the list. For instance, if
    you make a list request and receive 100 objects, ending with obj_foo, your
    subsequent call can include after=obj_foo in order to fetch the next page of the
    list.
    """

    limit: int
    """A limit on the number of objects to be returned.

    Limit can range between 1 and 100, and the default is 20.
    """

    owner_project_access: Literal["active", "inactive", "any"]
    """
    Filter API keys by whether the owner currently has effective access to the
    project. Use `active` for owners with access, `inactive` for owners without
    access, or `any` for all enabled project API keys. If omitted, the endpoint
    applies its existing membership-based visibility rules, which may exclude some
    enabled keys.
    """
