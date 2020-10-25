from openai.api_resources.abstract import (
    APIResource,
    CreateableAPIResource,
    DeletableAPIResource,
    ListableAPIResource,
    UpdateableAPIResource,
)


class CompletionConfig(
    CreateableAPIResource, ListableAPIResource, DeletableAPIResource
):
    OBJECT_NAME = "experimental.completion_config"
