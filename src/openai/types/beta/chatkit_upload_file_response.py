# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .file_part import FilePart
from .image_part import ImagePart

__all__ = ["ChatKitUploadFileResponse"]

ChatKitUploadFileResponse: TypeAlias = Annotated[Union[FilePart, ImagePart], PropertyInfo(discriminator="type")]
