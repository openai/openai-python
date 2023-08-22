from urllib.parse import quote_plus

from openai import error
from openai.api_resources.abstract import (
    CreateableAPIResource,
    PaginatableAPIResource,
    nested_resource_class_methods,
)
from openai.api_resources.abstract.deletable_api_resource import DeletableAPIResource
from openai.util import ApiType


@nested_resource_class_methods("event", operations=["paginated_list"])
class FineTuningJob(
    PaginatableAPIResource, CreateableAPIResource, DeletableAPIResource
):
    OBJECT_NAME = "fine_tuning.jobs"

    @classmethod
    def _prepare_cancel(
        cls,
        id,
        api_key=None,
        api_type=None,
        request_id=None,
        api_version=None,
        **params,
    ):
        base = cls.class_url()
        extn = quote_plus(id)

        typed_api_type, api_version = cls._get_api_type_and_version(
            api_type, api_version
        )
        if typed_api_type in (ApiType.AZURE, ApiType.AZURE_AD):
            url = "/%s%s/%s/cancel?api-version=%s" % (
                cls.azure_api_prefix,
                base,
                extn,
                api_version,
            )
        elif typed_api_type == ApiType.OPEN_AI:
            url = "%s/%s/cancel" % (base, extn)
        else:
            raise error.InvalidAPIType("Unsupported API type %s" % api_type)

        instance = cls(id, api_key, **params)
        return instance, url

    @classmethod
    def cancel(
        cls,
        id,
        api_key=None,
        api_type=None,
        request_id=None,
        api_version=None,
        **params,
    ):
        instance, url = cls._prepare_cancel(
            id,
            api_key,
            api_type,
            request_id,
            api_version,
            **params,
        )
        return instance.request("post", url, request_id=request_id)

    @classmethod
    def acancel(
        cls,
        id,
        api_key=None,
        api_type=None,
        request_id=None,
        api_version=None,
        **params,
    ):
        instance, url = cls._prepare_cancel(
            id,
            api_key,
            api_type,
            request_id,
            api_version,
            **params,
        )
        return instance.arequest("post", url, request_id=request_id)
