# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ...._utils import PropertyInfo
from .one_time_automation import OneTimeAutomation
from .periodic_automation import PeriodicAutomation

__all__ = ["Automation"]

Automation: TypeAlias = Annotated[Union[PeriodicAutomation, OneTimeAutomation], PropertyInfo(discriminator="type")]
