from openai.api_resources.abstract import (
    ListableAPIResource,
    CreateableAPIResource,
    nested_resource_class_methods,
)
from openai.six.moves.urllib.parse import quote_plus
from openai import util


@nested_resource_class_methods("event", operations=["list"])
class FineTune(ListableAPIResource, CreateableAPIResource):
    OBJECT_NAME = "fine-tune"

    @classmethod
    def cancel(cls, id, api_key=None, request_id=None, **params):
        base = cls.class_url()
        extn = quote_plus(id)
        url = "%s/%s/cancel" % (base, extn)
        instance = cls(id, api_key, **params)
        headers = util.populate_headers(request_id=request_id)
        return instance.request("post", url, headers=headers)