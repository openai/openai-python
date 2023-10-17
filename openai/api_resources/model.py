from openai.api_resources.abstract import DeletableAPIResource, ListableAPIResource
{
  "context_limit": {
    "type": "integer",
    "description": "The maximum context length that the model can effectively handle."
  },
}
class Model(ListableAPIResource, DeletableAPIResource):
    OBJECT_NAME = "models"
