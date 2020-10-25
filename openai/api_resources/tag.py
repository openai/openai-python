from __future__ import absolute_import, division, print_function

from openai.api_resources.abstract import (
    APIResource,
    CreateableAPIResource,
    DeletableAPIResource,
    ListableAPIResource,
    UpdateableAPIResource,
)


class Tag(
    CreateableAPIResource,
    UpdateableAPIResource,
    ListableAPIResource,
    DeletableAPIResource,
):
    OBJECT_NAME = "tag"
