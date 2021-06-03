from urllib.parse import quote_plus

from openai import api_requestor, error, util
from openai.openai_object import OpenAIObject


class APIResource(OpenAIObject):
    api_prefix = "v1"

    @classmethod
    def retrieve(cls, id, api_key=None, request_id=None, **params):
        instance = cls(id, api_key, **params)
        instance.refresh(request_id=request_id)
        return instance

    def refresh(self, request_id=None):
        headers = util.populate_headers(request_id=request_id)
        self.refresh_from(self.request("get", self.instance_url(), headers=headers))
        return self

    @classmethod
    def class_url(cls):
        if cls == APIResource:
            raise NotImplementedError(
                "APIResource is an abstract class.  You should perform "
                "actions on its subclasses (e.g. Charge, Customer)"
            )
        # Namespaces are separated in object names with periods (.) and in URLs
        # with forward slashes (/), so replace the former with the latter.
        base = cls.OBJECT_NAME.replace(".", "/")  # type: ignore
        return "/%s/%ss" % (cls.api_prefix, base)

    def instance_url(self):
        id = self.get("id")

        if not isinstance(id, str):
            raise error.InvalidRequestError(
                "Could not determine which URL to request: %s instance "
                "has invalid ID: %r, %s. ID should be of type `str` (or"
                " `unicode`)" % (type(self).__name__, id, type(id)),
                "id",
            )

        base = self.class_url()
        extn = quote_plus(id)
        return "%s/%s" % (base, extn)

    # The `method_` and `url_` arguments are suffixed with an underscore to
    # avoid conflicting with actual request parameters in `params`.
    @classmethod
    def _static_request(
        cls,
        method_,
        url_,
        api_key=None,
        api_base=None,
        idempotency_key=None,
        request_id=None,
        api_version=None,
        organization=None,
        **params,
    ):
        requestor = api_requestor.APIRequestor(
            api_key,
            api_version=api_version,
            organization=organization,
            api_base=api_base,
        )
        headers = util.populate_headers(idempotency_key, request_id)
        response, _, api_key = requestor.request(method_, url_, params, headers)
        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )
