# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ...._utils import PropertyInfo
from ...._models import BaseModel

__all__ = [
    "UsageVectorStoresResponse",
    "Data",
    "DataResult",
    "DataResultOrganizationUsageCompletionsResult",
    "DataResultOrganizationUsageEmbeddingsResult",
    "DataResultOrganizationUsageModerationsResult",
    "DataResultOrganizationUsageImagesResult",
    "DataResultOrganizationUsageAudioSpeechesResult",
    "DataResultOrganizationUsageAudioTranscriptionsResult",
    "DataResultOrganizationUsageVectorStoresResult",
    "DataResultOrganizationUsageCodeInterpreterSessionsResult",
    "DataResultOrganizationCostsResult",
    "DataResultOrganizationCostsResultAmount",
]


class DataResultOrganizationUsageCompletionsResult(BaseModel):
    """The aggregated completions usage details of the specific time bucket."""

    input_tokens: int
    """The aggregated number of text input tokens used, including cached tokens.

    For customers subscribe to scale tier, this includes scale tier tokens.
    """

    num_model_requests: int
    """The count of requests made to the model."""

    object: Literal["organization.usage.completions.result"]

    output_tokens: int
    """The aggregated number of text output tokens used.

    For customers subscribe to scale tier, this includes scale tier tokens.
    """

    api_key_id: Optional[str] = None
    """
    When `group_by=api_key_id`, this field provides the API key ID of the grouped
    usage result.
    """

    batch: Optional[bool] = None
    """
    When `group_by=batch`, this field tells whether the grouped usage result is
    batch or not.
    """

    input_audio_tokens: Optional[int] = None
    """The aggregated number of audio input tokens used, including cached tokens."""

    input_cached_tokens: Optional[int] = None
    """
    The aggregated number of text input tokens that has been cached from previous
    requests. For customers subscribe to scale tier, this includes scale tier
    tokens.
    """

    model: Optional[str] = None
    """
    When `group_by=model`, this field provides the model name of the grouped usage
    result.
    """

    output_audio_tokens: Optional[int] = None
    """The aggregated number of audio output tokens used."""

    project_id: Optional[str] = None
    """
    When `group_by=project_id`, this field provides the project ID of the grouped
    usage result.
    """

    service_tier: Optional[str] = None
    """
    When `group_by=service_tier`, this field provides the service tier of the
    grouped usage result.
    """

    user_id: Optional[str] = None
    """
    When `group_by=user_id`, this field provides the user ID of the grouped usage
    result.
    """


class DataResultOrganizationUsageEmbeddingsResult(BaseModel):
    """The aggregated embeddings usage details of the specific time bucket."""

    input_tokens: int
    """The aggregated number of input tokens used."""

    num_model_requests: int
    """The count of requests made to the model."""

    object: Literal["organization.usage.embeddings.result"]

    api_key_id: Optional[str] = None
    """
    When `group_by=api_key_id`, this field provides the API key ID of the grouped
    usage result.
    """

    model: Optional[str] = None
    """
    When `group_by=model`, this field provides the model name of the grouped usage
    result.
    """

    project_id: Optional[str] = None
    """
    When `group_by=project_id`, this field provides the project ID of the grouped
    usage result.
    """

    user_id: Optional[str] = None
    """
    When `group_by=user_id`, this field provides the user ID of the grouped usage
    result.
    """


class DataResultOrganizationUsageModerationsResult(BaseModel):
    """The aggregated moderations usage details of the specific time bucket."""

    input_tokens: int
    """The aggregated number of input tokens used."""

    num_model_requests: int
    """The count of requests made to the model."""

    object: Literal["organization.usage.moderations.result"]

    api_key_id: Optional[str] = None
    """
    When `group_by=api_key_id`, this field provides the API key ID of the grouped
    usage result.
    """

    model: Optional[str] = None
    """
    When `group_by=model`, this field provides the model name of the grouped usage
    result.
    """

    project_id: Optional[str] = None
    """
    When `group_by=project_id`, this field provides the project ID of the grouped
    usage result.
    """

    user_id: Optional[str] = None
    """
    When `group_by=user_id`, this field provides the user ID of the grouped usage
    result.
    """


class DataResultOrganizationUsageImagesResult(BaseModel):
    """The aggregated images usage details of the specific time bucket."""

    images: int
    """The number of images processed."""

    num_model_requests: int
    """The count of requests made to the model."""

    object: Literal["organization.usage.images.result"]

    api_key_id: Optional[str] = None
    """
    When `group_by=api_key_id`, this field provides the API key ID of the grouped
    usage result.
    """

    model: Optional[str] = None
    """
    When `group_by=model`, this field provides the model name of the grouped usage
    result.
    """

    project_id: Optional[str] = None
    """
    When `group_by=project_id`, this field provides the project ID of the grouped
    usage result.
    """

    size: Optional[str] = None
    """
    When `group_by=size`, this field provides the image size of the grouped usage
    result.
    """

    source: Optional[str] = None
    """
    When `group_by=source`, this field provides the source of the grouped usage
    result, possible values are `image.generation`, `image.edit`, `image.variation`.
    """

    user_id: Optional[str] = None
    """
    When `group_by=user_id`, this field provides the user ID of the grouped usage
    result.
    """


class DataResultOrganizationUsageAudioSpeechesResult(BaseModel):
    """The aggregated audio speeches usage details of the specific time bucket."""

    characters: int
    """The number of characters processed."""

    num_model_requests: int
    """The count of requests made to the model."""

    object: Literal["organization.usage.audio_speeches.result"]

    api_key_id: Optional[str] = None
    """
    When `group_by=api_key_id`, this field provides the API key ID of the grouped
    usage result.
    """

    model: Optional[str] = None
    """
    When `group_by=model`, this field provides the model name of the grouped usage
    result.
    """

    project_id: Optional[str] = None
    """
    When `group_by=project_id`, this field provides the project ID of the grouped
    usage result.
    """

    user_id: Optional[str] = None
    """
    When `group_by=user_id`, this field provides the user ID of the grouped usage
    result.
    """


class DataResultOrganizationUsageAudioTranscriptionsResult(BaseModel):
    """The aggregated audio transcriptions usage details of the specific time bucket."""

    num_model_requests: int
    """The count of requests made to the model."""

    object: Literal["organization.usage.audio_transcriptions.result"]

    seconds: int
    """The number of seconds processed."""

    api_key_id: Optional[str] = None
    """
    When `group_by=api_key_id`, this field provides the API key ID of the grouped
    usage result.
    """

    model: Optional[str] = None
    """
    When `group_by=model`, this field provides the model name of the grouped usage
    result.
    """

    project_id: Optional[str] = None
    """
    When `group_by=project_id`, this field provides the project ID of the grouped
    usage result.
    """

    user_id: Optional[str] = None
    """
    When `group_by=user_id`, this field provides the user ID of the grouped usage
    result.
    """


class DataResultOrganizationUsageVectorStoresResult(BaseModel):
    """The aggregated vector stores usage details of the specific time bucket."""

    object: Literal["organization.usage.vector_stores.result"]

    usage_bytes: int
    """The vector stores usage in bytes."""

    project_id: Optional[str] = None
    """
    When `group_by=project_id`, this field provides the project ID of the grouped
    usage result.
    """


class DataResultOrganizationUsageCodeInterpreterSessionsResult(BaseModel):
    """
    The aggregated code interpreter sessions usage details of the specific time bucket.
    """

    num_sessions: int
    """The number of code interpreter sessions."""

    object: Literal["organization.usage.code_interpreter_sessions.result"]

    project_id: Optional[str] = None
    """
    When `group_by=project_id`, this field provides the project ID of the grouped
    usage result.
    """


class DataResultOrganizationCostsResultAmount(BaseModel):
    """The monetary value in its associated currency."""

    currency: Optional[str] = None
    """Lowercase ISO-4217 currency e.g. "usd" """

    value: Optional[float] = None
    """The numeric value of the cost."""


class DataResultOrganizationCostsResult(BaseModel):
    """The aggregated costs details of the specific time bucket."""

    object: Literal["organization.costs.result"]

    amount: Optional[DataResultOrganizationCostsResultAmount] = None
    """The monetary value in its associated currency."""

    api_key_id: Optional[str] = None
    """
    When `group_by=api_key_id`, this field provides the API Key ID of the grouped
    costs result.
    """

    line_item: Optional[str] = None
    """
    When `group_by=line_item`, this field provides the line item of the grouped
    costs result.
    """

    project_id: Optional[str] = None
    """
    When `group_by=project_id`, this field provides the project ID of the grouped
    costs result.
    """

    quantity: Optional[float] = None
    """
    When `group_by=line_item`, this field provides the quantity of the grouped costs
    result.
    """


DataResult: TypeAlias = Annotated[
    Union[
        DataResultOrganizationUsageCompletionsResult,
        DataResultOrganizationUsageEmbeddingsResult,
        DataResultOrganizationUsageModerationsResult,
        DataResultOrganizationUsageImagesResult,
        DataResultOrganizationUsageAudioSpeechesResult,
        DataResultOrganizationUsageAudioTranscriptionsResult,
        DataResultOrganizationUsageVectorStoresResult,
        DataResultOrganizationUsageCodeInterpreterSessionsResult,
        DataResultOrganizationCostsResult,
    ],
    PropertyInfo(discriminator="object"),
]


class Data(BaseModel):
    end_time: int

    object: Literal["bucket"]

    results: List[DataResult]

    start_time: int


class UsageVectorStoresResponse(BaseModel):
    data: List[Data]

    has_more: bool

    next_page: Optional[str] = None

    object: Literal["page"]
