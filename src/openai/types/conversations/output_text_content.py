# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from .lob_prob import LobProb
from ..._models import BaseModel
from .url_citation_body import URLCitationBody
from .file_citation_body import FileCitationBody
from .container_file_citation_body import ContainerFileCitationBody

__all__ = ["OutputTextContent", "Annotation"]

Annotation: TypeAlias = Annotated[
    Union[FileCitationBody, URLCitationBody, ContainerFileCitationBody], PropertyInfo(discriminator="type")
]


class OutputTextContent(BaseModel):
    annotations: List[Annotation]
    """The annotations of the text output."""

    text: str
    """The text output from the model."""

    type: Literal["output_text"]
    """The type of the output text. Always `output_text`."""

    logprobs: Optional[List[LobProb]] = None
