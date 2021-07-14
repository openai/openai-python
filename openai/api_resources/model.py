from openai.api_resources.abstract import (
    ListableAPIResource,
    DeletableAPIResource,
)


class Model(ListableAPIResource, DeletableAPIResource):
    engine_required = False
    OBJECT_NAME = "model"
