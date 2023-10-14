from typing import Any, List

import openai
from openai import api_requestor, util
from openai.api_resources.abstract import APIResource


class Audio(APIResource):
    OBJECT_NAME = "audio"

    @classmethod
    def _get_url(cls, action, deployment_id=None, api_type=None, api_version=None):
        if api_type in (util.ApiType.AZURE, util.ApiType.AZURE_AD):
            return f"/{cls.azure_api_prefix}/deployments/{deployment_id}/audio/{action}?api-version={api_version}"
        return cls.class_url() + f"/{action}"

    @classmethod
    def _prepare_request(
        cls,
        file,
        filename,
        model,
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
        files: List[Any] = []
        data = {
            "model": model,
            **params,
        }
        files.append(("file", (filename, file, "application/octet-stream")))
        return requestor, files, data

    @classmethod
    def transcribe(
        cls,
        model,
        file,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        *,
        deployment_id=None,
        **params,
    ):
        requestor, files, data = cls._prepare_request(
            file=file,
            filename=file.name,
            model=model,
            api_key=api_key,
            api_base=api_base,
            api_type=api_type,
            api_version=api_version,
            organization=organization,
            **params,
        )
        api_type, api_version = cls._get_api_type_and_version(api_type, api_version)
        url = cls._get_url("transcriptions", deployment_id=deployment_id, api_type=api_type, api_version=api_version)
        response, _, api_key = requestor.request("post", url, files=files, params=data)
        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )

    @classmethod
    def translate(
        cls,
        model,
        file,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        *,
        deployment_id=None,
        **params,
    ):
        requestor, files, data = cls._prepare_request(
            file=file,
            filename=file.name,
            model=model,
            api_key=api_key,
            api_base=api_base,
            api_type=api_type,
            api_version=api_version,
            organization=organization,
            **params,
        )
        api_type, api_version = cls._get_api_type_and_version(api_type, api_version)
        url = cls._get_url("translations", deployment_id=deployment_id, api_type=api_type, api_version=api_version)
        response, _, api_key = requestor.request("post", url, files=files, params=data)
        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )

    @classmethod
    def transcribe_raw(
        cls,
        model,
        file,
        filename,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        *,
        deployment_id=None,
        **params,
    ):
        requestor, files, data = cls._prepare_request(
            file=file,
            filename=filename,
            model=model,
            api_key=api_key,
            api_base=api_base,
            api_type=api_type,
            api_version=api_version,
            organization=organization,
            **params,
        )
        api_type, api_version = cls._get_api_type_and_version(api_type, api_version)
        url = cls._get_url("transcriptions", deployment_id=deployment_id, api_type=api_type, api_version=api_version)
        response, _, api_key = requestor.request("post", url, files=files, params=data)
        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )

    @classmethod
    def translate_raw(
        cls,
        model,
        file,
        filename,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        *,
        deployment_id=None,
        **params,
    ):
        requestor, files, data = cls._prepare_request(
            file=file,
            filename=filename,
            model=model,
            api_key=api_key,
            api_base=api_base,
            api_type=api_type,
            api_version=api_version,
            organization=organization,
            **params,
        )
        api_type, api_version = cls._get_api_type_and_version(api_type, api_version)
        url = cls._get_url("translations", deployment_id=deployment_id, api_type=api_type, api_version=api_version)
        response, _, api_key = requestor.request("post", url, files=files, params=data)
        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )

    @classmethod
    async def atranscribe(
        cls,
        model,
        file,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        *,
        deployment_id=None,
        **params,
    ):
        requestor, files, data = cls._prepare_request(
            file=file,
            filename=file.name,
            model=model,
            api_key=api_key,
            api_base=api_base,
            api_type=api_type,
            api_version=api_version,
            organization=organization,
            **params,
        )
        api_type, api_version = cls._get_api_type_and_version(api_type, api_version)
        url = cls._get_url("transcriptions", deployment_id=deployment_id, api_type=api_type, api_version=api_version)
        response, _, api_key = await requestor.arequest(
            "post", url, files=files, params=data
        )
        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )

    @classmethod
    async def atranslate(
        cls,
        model,
        file,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        *,
        deployment_id=None,
        **params,
    ):
        requestor, files, data = cls._prepare_request(
            file=file,
            filename=file.name,
            model=model,
            api_key=api_key,
            api_base=api_base,
            api_type=api_type,
            api_version=api_version,
            organization=organization,
            **params,
        )
        api_type, api_version = cls._get_api_type_and_version(api_type, api_version)
        url = cls._get_url("translations", deployment_id=deployment_id, api_type=api_type, api_version=api_version)
        response, _, api_key = await requestor.arequest(
            "post", url, files=files, params=data
        )
        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )

    @classmethod
    async def atranscribe_raw(
        cls,
        model,
        file,
        filename,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        *,
        deployment_id=None,
        **params,
    ):
        requestor, files, data = cls._prepare_request(
            file=file,
            filename=filename,
            model=model,
            api_key=api_key,
            api_base=api_base,
            api_type=api_type,
            api_version=api_version,
            organization=organization,
            **params,
        )
        api_type, api_version = cls._get_api_type_and_version(api_type, api_version)
        url = cls._get_url("transcriptions", deployment_id=deployment_id, api_type=api_type, api_version=api_version)
        response, _, api_key = await requestor.arequest(
            "post", url, files=files, params=data
        )
        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )

    @classmethod
    async def atranslate_raw(
        cls,
        model,
        file,
        filename,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        *,
        deployment_id=None,
        **params,
    ):
        requestor, files, data = cls._prepare_request(
            file=file,
            filename=filename,
            model=model,
            api_key=api_key,
            api_base=api_base,
            api_type=api_type,
            api_version=api_version,
            organization=organization,
            **params,
        )
        api_type, api_version = cls._get_api_type_and_version(api_type, api_version)
        url = cls._get_url("translations", deployment_id=deployment_id, api_type=api_type, api_version=api_version)
        response, _, api_key = await requestor.arequest(
            "post", url, files=files, params=data
        )
        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )
