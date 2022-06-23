from openai.api_resources.abstract import DeletableAPIResource, ListableAPIResource


class Model(ListableAPIResource, DeletableAPIResource):
    engine_required = False
    OBJECT_NAME = "models"
