# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from pydantic import StrictInt, StrictStr, StrictBool, StrictFloat

from ....._utils import PropertyInfo
from ....._models import BaseModel

__all__ = ["FederationRule", "Permissions", "PermissionsServiceAccountDefault", "PermissionsRestricted"]


class PermissionsServiceAccountDefault(BaseModel):
    type: Literal["service_account_default"]


class PermissionsRestricted(BaseModel):
    scopes: List[str]

    type: Literal["restricted"]


Permissions: TypeAlias = Annotated[
    Union[PermissionsServiceAccountDefault, PermissionsRestricted], PropertyInfo(discriminator="type")
]


class FederationRule(BaseModel):
    id: str

    attribute_matchers: Dict[str, Union[StrictStr, StrictBool, StrictInt, StrictFloat]]

    created_at: int

    description: Optional[str] = None

    enabled: bool

    name: Optional[str] = None

    object: Literal["organization.workload_identity_federation_rule"]

    permissions: Permissions

    project_id: str

    service_account_id: str

    updated_at: int

    workload_identity_provider_id: str
