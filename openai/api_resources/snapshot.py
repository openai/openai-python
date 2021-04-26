from openai.api_resources.abstract import (
    ListableAPIResource,
    DeletableAPIResource,
)


class Snapshot(ListableAPIResource, DeletableAPIResource):
    engine_required = False
    OBJECT_NAME = "snapshot"
