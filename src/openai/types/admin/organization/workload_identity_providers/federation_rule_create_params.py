# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ....._types import SequenceNotStr

__all__ = ["FederationRuleCreateParams", "Permissions", "PermissionsServiceAccountDefault", "PermissionsRestricted"]


class FederationRuleCreateParams(TypedDict, total=False):
    attribute_matchers: Required[Dict[str, Union[str, bool, Union[int, float]]]]

    project_id: Required[str]

    service_account_id: Required[str]

    description: str

    enabled: bool

    name: str

    permissions: Permissions


class PermissionsServiceAccountDefault(TypedDict, total=False):
    type: Required[Literal["service_account_default"]]


class PermissionsRestricted(TypedDict, total=False):
    scopes: Required[SequenceNotStr[str]]

    type: Required[Literal["restricted"]]


Permissions: TypeAlias = Union[PermissionsServiceAccountDefault, PermissionsRestricted]
