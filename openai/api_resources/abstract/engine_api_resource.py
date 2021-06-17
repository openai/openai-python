import time
from typing import Optional
from urllib.parse import quote_plus

from openai import api_requestor, error, util
from openai.api_resources.abstract.api_resource import APIResource

MAX_TIMEOUT = 20


class EngineAPIResource(APIResource):
    engine_required = True
    plain_old_data = False

    def __init__(self, engine: Optional[str] = None, **kwargs):
        super().__init__(engine=engine, **kwargs)

    @classmethod
    def class_url(cls, engine: Optional[str] = None):
        # Namespaces are separated in object names with periods (.) and in URLs
        # with forward slashes (/), so replace the former with the latter.
        base = cls.OBJECT_NAME.replace(".", "/")  # type: ignore
        if engine is None:
            return "/%s/%ss" % (cls.api_prefix, base)

        extn = quote_plus(engine)
        return "/%s/engines/%s/%ss" % (cls.api_prefix, extn, base)

    @classmethod
    def create(
        cls,
        api_key=None,
        api_base=None,
        idempotency_key=None,
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
            api_version=api_version,
            organization=organization,
        )
        url = cls.class_url(engine)
        headers = util.populate_headers(idempotency_key, request_id)
        response, _, api_key = requestor.request(
            "post", url, params, headers, stream=stream
        )

        if stream:
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
                "Could not determine which URL to request: %s instance "
                "has invalid ID: %r, %s. ID should be of type `str` (or"
                " `unicode`)" % (type(self).__name__, id, type(id)),
                "id",
            )

        base = self.class_url(self.engine)
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
