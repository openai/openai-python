import abc
from urllib.parse import quote_plus
from typing import Union, Optional, AnyStr

from openai import error
from openai.api_resources.abstract.api_resource import APIResource
from openai.util import ApiType


class DeletableAPIResource(APIResource, abc.ABC):
    @classmethod
    def __prepare_delete(
        cls,
        sid: AnyStr,
        api_type: Optional[str] = None,
        api_version: Optional[str] = None,
    ):
        if isinstance(cls, APIResource):
            raise ValueError(".delete may only be called as a class method now.")

        base = cls.class_url()
        extn = quote_plus(sid)

        typed_api_type, api_version = cls._get_api_type_and_version(
            api_type, api_version
        )
        if typed_api_type in (ApiType.AZURE, ApiType.AZURE_AD):
            url = "/%s%s/%s?api-version=%s" % (
                cls.azure_api_prefix,
                base,
                extn,
                api_version,
            )
        elif typed_api_type == ApiType.OPEN_AI:
            url = "%s/%s" % (base, extn)
        else:
            raise error.InvalidAPIType("Unsupported API type %s" % api_type)
        return url

    @classmethod
    def delete(
            cls,
            sid: AnyStr,
            api_type: Optional[str] = None,
            api_version: Optional[str] = None,
            **params,
    ):
        url = cls.__prepare_delete(sid, api_type, api_version)

        return cls._static_request(
            "delete", url, api_type=api_type, api_version=api_version, **params
        )

    @classmethod
    def adelete(
            cls,
            sid: AnyStr,
            api_type: Optional[str] = None,
            api_version: Optional[str] = None,
            **params,
    ):
        url = cls.__prepare_delete(sid, api_type, api_version)

        return cls._astatic_request(
            "delete", url, api_type=api_type, api_version=api_version, **params
        )
