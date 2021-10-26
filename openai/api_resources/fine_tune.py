from urllib.parse import quote_plus

from openai import api_requestor, util
from openai.api_resources.abstract import (
    CreateableAPIResource,
    ListableAPIResource,
    nested_resource_class_methods,
)
from openai.openai_response import OpenAIResponse


@nested_resource_class_methods("event", operations=["list"])
class FineTune(ListableAPIResource, CreateableAPIResource):
    OBJECT_NAME = "fine-tune"

    @classmethod
    def cancel(cls, id, api_key=None, request_id=None, **params):
        base = cls.class_url()
        extn = quote_plus(id)
        url = "%s/%s/cancel" % (base, extn)
        instance = cls(id, api_key, **params)
        return instance.request("post", url, request_id=request_id)

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
        response, _, api_key = requestor.request(
            "get", url, params, stream=True, request_id=request_id
        )

        assert not isinstance(response, OpenAIResponse)  # must be an iterator
        return (
            util.convert_to_openai_object(
                line,
                api_key,
                api_version,
                organization,
            )
            for line in response
        )
