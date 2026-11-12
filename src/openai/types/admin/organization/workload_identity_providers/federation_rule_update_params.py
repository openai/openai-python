# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ....._types import SequenceNotStr

__all__ = [
    "FederationRuleUpdateParams",
    "Permissions",
    "PermissionsDefaultPermissionsParam",
    "PermissionsRestrictedPermissionsParam",
]


class FederationRuleUpdateParams(TypedDict, total=False):
    workload_identity_provider_id: Required[str]

    attribute_matchers: Dict[str, Union[str, bool, Union[int, float]]]

    description: Optional[str]

    enabled: bool

    name: Optional[str]

    permissions: Permissions


class PermissionsDefaultPermissionsParam(TypedDict, total=False):
    type: Required[Literal["service_account_default"]]


class PermissionsRestrictedPermissionsParam(TypedDict, total=False):
    scopes: Required[SequenceNotStr[str]]

    type: Required[Literal["restricted"]]


Permissions: TypeAlias = Union[PermissionsDefaultPermissionsParam, PermissionsRestrictedPermissionsParam]
