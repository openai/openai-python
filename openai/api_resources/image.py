# WARNING: This interface is considered experimental and may changed in the future without warning.
from typing import Any, List

import openai
from openai import api_requestor, util
from openai.api_resources.abstract import APIResource


class Image(APIResource):
    OBJECT_NAME = "images"

    @classmethod
    def _get_url(cls, action):
        return cls.class_url() + f"/{action}"

    @classmethod
    def create(
        cls,
        **params,
    ):
        instance = cls()
        return instance.request("post", cls._get_url("generations"), params)

    @classmethod
    def acreate(cls, **params):
        instance = cls()
        return instance.arequest("post", cls._get_url("generations"), params)

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
        _, api_version = cls._get_api_type_and_version(api_type, api_version)

        url = cls._get_url("variations")

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
        mask,
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
        _, api_version = cls._get_api_type_and_version(api_type, api_version)

        url = cls._get_url("edits")

        files: List[Any] = []
        for key, value in params.items():
            files.append((key, (None, value)))
        files.append(("image", ("image", image, "application/octet-stream")))
        files.append(("mask", ("mask", mask, "application/octet-stream")))
        return requestor, url, files

    @classmethod
    def create_edit(
        cls,
        image,
        mask,
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
        mask,
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
