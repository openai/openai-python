# WARNING: This interface is considered experimental and may changed in the future without warning.
from typing import Any, List

import openai
from openai import api_requestor, util
from openai.api_resources.abstract import APIResource
from openai.util import ApiType


class Image(APIResource):
    OBJECT_NAME = "images"

    _azure_preview_version = "2022-11-23-preview"

    @classmethod
    def _get_api_type_and_version(
        cls, api_type = None, api_version = None
    ):
        api_type, base_api_version = super()._get_api_type_and_version()
        if api_type in (ApiType.AZURE, ApiType.AZURE_AD):
            # This override is only temporary: DallE and GPT endpoint versioning is currently out of sync but will be aligned soon.
            return (api_type, api_version or Image._azure_preview_version)
        else:
            return (api_type, base_api_version)

    @classmethod
    def _get_url(cls, openai_action, azure_action, api_type, api_version):
        if api_type in (util.ApiType.AZURE, util.ApiType.AZURE_AD):
            return f"/{cls.azure_dalle_prefix}{cls.class_url()}/{azure_action}?api-version={api_version}"
        else:
            return cls.class_url() + f"/{openai_action}"
        
    @classmethod
    def _get_azure_operations_url(cls, operation_id, api_version):
        return f"/{cls.azure_dalle_prefix}/operations/{operation_id}?api-version={api_version}"

    @classmethod
    def create(
        cls,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        **params,
    ):
        requestor = api_requestor.APIRequestor(
            api_key,
            api_base=api_base or openai.api_base,
            api_type=api_type,
            api_version=api_version,
            organization=organization,
        )

        api_type, api_version = cls._get_api_type_and_version(api_type, api_version)

        response, _, api_key = requestor.request(
            "post", cls._get_url("generations", "generate", api_type=api_type, api_version=api_version), params
        )

        if api_type in (util.ApiType.AZURE, util.ApiType.AZURE_AD):
            url = cls._get_azure_operations_url(response.data['id'], api_version)
            response, _, api_key = requestor.poll(
                "get", url,
                until=lambda response: response.data["status"] not in ["NotStarted", "Running"],
                delay=response.retry_after
            )

        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )

    @classmethod
    async def acreate(
        cls,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        **params,
    ):

        requestor = api_requestor.APIRequestor(
            api_key,
            api_base=api_base or openai.api_base,
            api_type=api_type,
            api_version=api_version,
            organization=organization,
        )

        api_type, api_version = cls._get_api_type_and_version(api_type, api_version)

        response, _, api_key = await requestor.arequest(
            "post", cls._get_url("generations", "generate", api_type=api_type, api_version=api_version), params
        )

        if api_type in (util.ApiType.AZURE, util.ApiType.AZURE_AD):
            url = cls._get_azure_operations_url(response.data['id'], api_version)
            response, _, api_key = await requestor.apoll(
                "get", url,
                until=lambda response: response.data["status"] not in ["NotStarted", "Running"],
                delay=response.retry_after
            )

        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )

    @classmethod
    def _prepare_create_variation(
        cls,
        image,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        **params,
    ):
        requestor = api_requestor.APIRequestor(
            api_key,
            api_base=api_base or openai.api_base,
            api_type=api_type,
            api_version=api_version,
            organization=organization,
        )
        api_type, api_version = cls._get_api_type_and_version(api_type, api_version)

        url = cls._get_url("variations", None, api_type=api_type, api_version=api_version)

        files: List[Any] = []
        for key, value in params.items():
            files.append((key, (None, value)))
        files.append(("image", ("image", image, "application/octet-stream")))
        return requestor, url, files

    @classmethod
    def create_variation(
        cls,
        image,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        **params,
    ):
        requestor, url, files = cls._prepare_create_variation(
            image,
            api_key,
            api_base,
            api_type,
            api_version,
            organization,
            **params,
        )

        response, _, api_key = requestor.request("post", url, files=files)

        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )

    @classmethod
    async def acreate_variation(
        cls,
        image,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        **params,
    ):
        requestor, url, files = cls._prepare_create_variation(
            image,
            api_key,
            api_base,
            api_type,
            api_version,
            organization,
            **params,
        )

        response, _, api_key = await requestor.arequest("post", url, files=files)

        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )

    @classmethod
    def _prepare_create_edit(
        cls,
        image,
        mask=None,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        **params,
    ):
        requestor = api_requestor.APIRequestor(
            api_key,
            api_base=api_base or openai.api_base,
            api_type=api_type,
            api_version=api_version,
            organization=organization,
        )
        api_type, api_version = cls._get_api_type_and_version(api_type, api_version)

        url = cls._get_url("edits", None, api_type=api_type, api_version=api_version)

        files: List[Any] = []
        for key, value in params.items():
            files.append((key, (None, value)))
        files.append(("image", ("image", image, "application/octet-stream")))
        if mask is not None:
            files.append(("mask", ("mask", mask, "application/octet-stream")))
        return requestor, url, files

    @classmethod
    def create_edit(
        cls,
        image,
        mask=None,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        **params,
    ):
        requestor, url, files = cls._prepare_create_edit(
            image,
            mask,
            api_key,
            api_base,
            api_type,
            api_version,
            organization,
            **params,
        )

        response, _, api_key = requestor.request("post", url, files=files)

        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )

    @classmethod
    async def acreate_edit(
        cls,
        image,
        mask=None,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        **params,
    ):
        requestor, url, files = cls._prepare_create_edit(
            image,
            mask,
            api_key,
            api_base,
            api_type,
            api_version,
            organization,
            **params,
        )

        response, _, api_key = await requestor.arequest("post", url, files=files)

        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )
