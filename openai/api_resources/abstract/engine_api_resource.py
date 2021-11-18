import time
from typing import Optional
from urllib.parse import quote_plus

import openai
from openai import api_requestor, error, util
from openai.api_resources.abstract.api_resource import APIResource
from openai.openai_response import OpenAIResponse
from openai.util import ApiType

MAX_TIMEOUT = 20


class EngineAPIResource(APIResource):
    engine_required = True
    plain_old_data = False
    azure_api_prefix = 'openai/deployments'
    azure_api_version = '?api-version=2021-11-01-preview'

    def __init__(self, engine: Optional[str] = None, api_type : Optional[str] = None, **kwargs):
        self.api_type = api_type
        super().__init__(engine=engine, **kwargs)

    @classmethod
    def class_url(cls, engine: Optional[str] = None, api_type : Optional[str] = None):
        # Namespaces are separated in object names with periods (.) and in URLs
        # with forward slashes (/), so replace the former with the latter.
        base = cls.OBJECT_NAME.replace(".", "/")  # type: ignore
        typed_api_type = ApiType.from_str(api_type) if api_type else ApiType.from_str(openai.api_type)

        if typed_api_type == ApiType.AZURE:
            if engine is None:
                raise error.InvalidRequestError(
                    "Must provide an 'engine' parameter for API type: azure.", param="engine"
                )
            extn = quote_plus(engine)
            return "/%s/%s/%ss%s" % (cls.azure_api_prefix, extn, base, cls.azure_api_version)

        elif typed_api_type == ApiType.OPEN_AI:
            if engine is None:
                return "/%s/%ss" % (cls.api_prefix, base)

            extn = quote_plus(engine)
            return "/%s/engines/%s/%ss" % (cls.api_prefix, extn, base)

        else:
            raise error.InvalidAPIType('Unsupported API type %s' % api_type)

    @classmethod
    def create(
        cls,
        api_key=None,
        api_base=None,
        api_type=None,
        request_id=None,
        api_version=None,
        organization=None,
        **params,
    ):
        engine = params.pop("engine", None)
        timeout = params.pop("timeout", None)
        stream = params.get("stream", False)
        if engine is None and cls.engine_required:
            raise error.InvalidRequestError(
                "Must provide an 'engine' parameter to create a %s" % cls, "engine"
            )

        if timeout is None:
            # No special timeout handling
            pass
        elif timeout > 0:
            # API only supports timeouts up to MAX_TIMEOUT
            params["timeout"] = min(timeout, MAX_TIMEOUT)
            timeout = (timeout - params["timeout"]) or None
        elif timeout == 0:
            params["timeout"] = MAX_TIMEOUT

        requestor = api_requestor.APIRequestor(
            api_key,
            api_base=api_base,
            api_type=api_type,
            api_version=api_version,
            organization=organization,
        )
        url = cls.class_url(engine, api_type)
        response, _, api_key = requestor.request(
            "post", url, params, stream=stream, request_id=request_id
        )

        if stream:
            assert not isinstance(response, OpenAIResponse)  # must be an iterator
            return (
                util.convert_to_openai_object(
                    line,
                    api_key,
                    api_version,
                    organization,
                    engine=engine,
                    plain_old_data=cls.plain_old_data,
                )
                for line in response
            )
        else:
            obj = util.convert_to_openai_object(
                response,
                api_key,
                api_version,
                organization,
                engine=engine,
                plain_old_data=cls.plain_old_data,
            )

            if timeout is not None:
                obj.wait(timeout=timeout or None)

        return obj

    def instance_url(self):
        id = self.get("id")

        if not isinstance(id, str):
            raise error.InvalidRequestError(
                f"Could not determine which URL to request: {type(self).__name__} instance has invalid ID: {id}, {type(id)}. ID should be of type str.",
                "id",
            )

        base = self.class_url(self.engine, self.api_type)
        extn = quote_plus(id)
        url = "%s/%s" % (base, extn)

        timeout = self.get("timeout")
        if timeout is not None:
            timeout = quote_plus(str(timeout))
            url += "?timeout={}".format(timeout)
        return url

    def wait(self, timeout=None):
        start = time.time()
        while self.status != "complete":
            self.timeout = (
                min(timeout + start - time.time(), MAX_TIMEOUT)
                if timeout is not None
                else MAX_TIMEOUT
            )
            if self.timeout < 0:
                del self.timeout
                break
            self.refresh()
        return self
