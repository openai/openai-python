from openai import api_requestor, util
from openai.api_resources.abstract.api_resource import APIResource


class CreateableAPIResource(APIResource):
    plain_old_data = False

    @classmethod
    def create(
        cls,
        api_key=None,
        api_base=None,
        request_id=None,
        api_version=None,
        organization=None,
        **params,
    ):
        requestor = api_requestor.APIRequestor(
            api_key,
            api_base=api_base,
            api_version=api_version,
            organization=organization,
        )
        url = cls.class_url()
        response, _, api_key = requestor.request(
            "post", url, params, request_id=request_id
        )

        return util.convert_to_openai_object(
            response,
            api_key,
            api_version,
            organization,
            plain_old_data=cls.plain_old_data,
        )
