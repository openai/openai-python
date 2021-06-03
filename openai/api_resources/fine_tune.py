from urllib.parse import quote_plus

from openai.api_resources.abstract import (
    ListableAPIResource,
    CreateableAPIResource,
    nested_resource_class_methods,
)
from openai import api_requestor, util


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

    @classmethod
    def stream_events(
        cls,
        id,
        api_key=None,
        api_base=None,
        request_id=None,
        api_version=None,
        organization=None,
        **params,
    ):
        base = cls.class_url()
        extn = quote_plus(id)

        requestor = api_requestor.APIRequestor(
            api_key,
            api_base=api_base,
            api_version=api_version,
            organization=organization,
        )
        url = "%s/%s/events?stream=true" % (base, extn)
        headers = util.populate_headers(request_id=request_id)
        response, _, api_key = requestor.request(
            "get", url, params, headers=headers, stream=True
        )

        return (
            util.convert_to_openai_object(
                line,
                api_key,
                api_version,
                organization,
            )
            for line in response
        )
