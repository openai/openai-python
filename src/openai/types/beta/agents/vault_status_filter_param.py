# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import TypeAlias

from .vault_status import VaultStatus

__all__ = ["VaultStatusFilterParam"]

VaultStatusFilterParam: TypeAlias = Union[VaultStatus, Iterable[VaultStatus]]
