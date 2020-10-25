from openai.api_resources.abstract.engine_api_resource import EngineAPIResource
from openai.api_resources.abstract import ListableAPIResource, DeletableAPIResource


class Snapshot(EngineAPIResource, ListableAPIResource, DeletableAPIResource):
    engine_required = False
    OBJECT_NAME = "snapshot"
