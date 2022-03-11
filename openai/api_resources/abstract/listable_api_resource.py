from openai import api_requestor, util
from openai.api_resources.abstract.api_resource import APIResource


class ListableAPIResource(APIResource):
    @classmethod
    def auto_paging_iter(cls, *args, **params):
        return cls.list(*args, **params).auto_paging_iter()

    @classmethod
    def list(
        cls,
        api_key=None,
        request_id=None,
        api_version=None,
        organization=None,
        api_base=None,
        **params,
    ):
        requestor = api_requestor.APIRequestor(
            api_key,
            api_base=api_base or cls.api_base(),
            api_version=api_version,
            organization=organization,
        )
        url = cls.class_url()
        response, _, api_key = requestor.request(
            "get", url, params, request_id=request_id
        )
        openai_object = util.convert_to_openai_object(
            response, api_key, api_version, organization
        )
        openai_object._retrieve_params = params
        return openai_object
