from urllib.parse import quote_plus

from openai import api_requestor, error, util
import openai
from openai.openai_object import OpenAIObject
from openai.util import ApiType


class APIResource(OpenAIObject):
    api_prefix = ""
    azure_api_prefix = 'openai/deployments'

    @classmethod
    def retrieve(cls, id, api_key=None, request_id=None, **params):
        instance = cls(id, api_key, **params)
        instance.refresh(request_id=request_id)
        return instance

    def refresh(self, request_id=None):
        self.refresh_from(
            self.request("get", self.instance_url(), request_id=request_id)
        )
        return self

    @classmethod
    def class_url(cls):
        if cls == APIResource:
            raise NotImplementedError(
                "APIResource is an abstract class. You should perform actions on its subclasses."
            )
        # Namespaces are separated in object names with periods (.) and in URLs
        # with forward slashes (/), so replace the former with the latter.
        base = cls.OBJECT_NAME.replace(".", "/")  # type: ignore
        if cls.api_prefix:
            return "/%s/%ss" % (cls.api_prefix, base)
        return "/%ss" % (base)

    def instance_url(self, operation=None):
        id = self.get("id")

        if not isinstance(id, str):
            raise error.InvalidRequestError(
                "Could not determine which URL to request: %s instance "
                "has invalid ID: %r, %s. ID should be of type `str` (or"
                " `unicode`)" % (type(self).__name__, id, type(id)),
                "id",
            )
        api_version = self.api_version or openai.api_version

        if self.typed_api_type == ApiType.AZURE:
            if not api_version:
                raise error.InvalidRequestError("An API version is required for the Azure API type.")
            if not operation:
                raise error.InvalidRequestError(
                    "The request needs an operation (eg: 'search') for the Azure OpenAI API type."
                )
            extn = quote_plus(id)
            return "/%s/%s/%s?api-version=%s" % (self.azure_api_prefix, extn, operation, api_version)

        elif self.typed_api_type == ApiType.OPEN_AI:
            base = self.class_url()
            extn = quote_plus(id)
            return "%s/%s" % (base, extn)

        else:
            raise error.InvalidAPIType('Unsupported API type %s' % self.api_type)
    

    # The `method_` and `url_` arguments are suffixed with an underscore to
    # avoid conflicting with actual request parameters in `params`.
    @classmethod
    def _static_request(
        cls,
        method_,
        url_,
        api_key=None,
        api_base=None,
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
        response, _, api_key = requestor.request(
            method_, url_, params, request_id=request_id
        )
        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )
