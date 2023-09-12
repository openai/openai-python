from typing import Any, List, overload

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

    @overload
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
        **params,
    ):
        ...

    @overload
    @classmethod
    def transcribe(
        cls,
        *,
        deployment_id=None,
        file=None,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        **params,
    ):
        ...

    @classmethod
    def transcribe(
        cls,
        *args,
        **params,
    ):
        if len(args) > 7:
            raise TypeError(
                f"transcribe() takes from 3 to 8 positional arguments but {len(args)+1} were given"
            )
        util.check_required(*args, method_name="transcribe", required=["model", "file"], **params)

        positional = list(args)
        model =  positional.pop(0) if positional else params.pop("model", None)
        file = positional.pop(0) if positional else params.pop("file", None)
        api_key = positional.pop(0) if positional else params.pop("api_key", None)
        api_base = positional.pop(0) if positional else params.pop("api_base", None)
        api_type = positional.pop(0) if positional else params.pop("api_type", None)
        api_version = positional.pop(0) if positional else params.pop("api_version", None)
        organization = positional.pop(0) if positional else params.pop("organization", None)
        deployment_id = params.pop("deployment_id", None)

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

    @overload
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
        **params,
    ):
        ...


    @overload
    @classmethod
    def translate(
        cls,
        *,
        deployment_id=None,
        file=None,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        **params,
    ):
        ...

    @classmethod
    def translate(
        cls,
        *args,
        **params,
    ):
        if len(args) > 7:
            raise TypeError(
                f"translate() takes from 3 to 8 positional arguments but {len(args)+1} were given"
            )
        util.check_required(*args, method_name="translate", required=["model", "file"], **params)

        positional = list(args)
        model =  positional.pop(0) if positional else params.pop("model", None)
        file = positional.pop(0) if positional else params.pop("file", None)
        api_key = positional.pop(0) if positional else params.pop("api_key", None)
        api_base = positional.pop(0) if positional else params.pop("api_base", None)
        api_type = positional.pop(0) if positional else params.pop("api_type", None)
        api_version = positional.pop(0) if positional else params.pop("api_version", None)
        organization = positional.pop(0) if positional else params.pop("organization", None)
        deployment_id = params.pop("deployment_id", None)

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

    @overload
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
        **params,
    ):
        ...


    @overload
    @classmethod
    def transcribe_raw(
        cls,
        *,
        deployment_id=None,
        file=None,
        filename=None,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        **params,
    ):
        ...

    @classmethod
    def transcribe_raw(
        cls,
        *args,
        **params,
    ):
        if len(args) > 8:
            raise TypeError(
                f"transcribe_raw() takes from 4 to 9 positional arguments but {len(args)+1} were given"
            )
        util.check_required(*args, method_name="transcribe_raw", required=["model", "file", "filename"], **params)

        positional = list(args)
        model =  positional.pop(0) if positional else params.pop("model", None)
        file = positional.pop(0) if positional else params.pop("file", None)
        filename = positional.pop(0) if positional else params.pop("filename", None)
        api_key = positional.pop(0) if positional else params.pop("api_key", None)
        api_base = positional.pop(0) if positional else params.pop("api_base", None)
        api_type = positional.pop(0) if positional else params.pop("api_type", None)
        api_version = positional.pop(0) if positional else params.pop("api_version", None)
        organization = positional.pop(0) if positional else params.pop("organization", None)
        deployment_id = params.pop("deployment_id", None)

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

    @overload
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
        **params,
    ):
        ...

    @overload
    @classmethod
    def translate_raw(
        cls,
        *,
        deployment_id=None,
        file=None,
        filename=None,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        **params,
    ):
        ...

    @classmethod
    def translate_raw(
        cls,
        *args,
        **params,
    ):
        if len(args) > 8:
            raise TypeError(
                f"translate_raw() takes from 4 to 9 positional arguments but {len(args)+1} were given"
            )
        util.check_required(*args, method_name="translate_raw", required=["model", "file", "filename"], **params)

        positional = list(args)
        model =  positional.pop(0) if positional else params.pop("model", None)
        file = positional.pop(0) if positional else params.pop("file", None)
        filename = positional.pop(0) if positional else params.pop("filename", None)
        api_key = positional.pop(0) if positional else params.pop("api_key", None)
        api_base = positional.pop(0) if positional else params.pop("api_base", None)
        api_type = positional.pop(0) if positional else params.pop("api_type", None)
        api_version = positional.pop(0) if positional else params.pop("api_version", None)
        organization = positional.pop(0) if positional else params.pop("organization", None)
        deployment_id = params.pop("deployment_id", None)

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

    @overload
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
        **params,
    ):
        ...

    @overload
    @classmethod
    async def atranscribe(
        cls,
        *,
        deployment_id=None,
        file=None,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        **params,
    ):
        ...

    @classmethod
    async def atranscribe(
        cls,
        *args,
        **params,
    ):
        if len(args) > 7:
            raise TypeError(
                f"atranscribe() takes from 3 to 8 positional arguments but {len(args)+1} were given"
            )
        util.check_required(*args, method_name="atranscribe", required=["model", "file"], **params)

        positional = list(args)
        model =  positional.pop(0) if positional else params.pop("model", None)
        file = positional.pop(0) if positional else params.pop("file", None)
        api_key = positional.pop(0) if positional else params.pop("api_key", None)
        api_base = positional.pop(0) if positional else params.pop("api_base", None)
        api_type = positional.pop(0) if positional else params.pop("api_type", None)
        api_version = positional.pop(0) if positional else params.pop("api_version", None)
        organization = positional.pop(0) if positional else params.pop("organization", None)
        deployment_id = params.pop("deployment_id", None)

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

    @overload
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
        **params,
    ):
        ...

    @overload
    @classmethod
    async def atranslate(
        cls,
        *,
        deployment_id=None,
        file=None,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        **params,
    ):
        ...

    @classmethod
    async def atranslate(
        cls,
        *args,
        **params,
    ):
        if len(args) > 7:
            raise TypeError(
                f"atranslate() takes from 3 to 8 positional arguments but {len(args)+1} were given"
            )
        util.check_required(*args, method_name="atranslate", required=["model", "file"], **params)

        positional = list(args)
        model =  positional.pop(0) if positional else params.pop("model", None)
        file = positional.pop(0) if positional else params.pop("file", None)
        api_key = positional.pop(0) if positional else params.pop("api_key", None)
        api_base = positional.pop(0) if positional else params.pop("api_base", None)
        api_type = positional.pop(0) if positional else params.pop("api_type", None)
        api_version = positional.pop(0) if positional else params.pop("api_version", None)
        organization = positional.pop(0) if positional else params.pop("organization", None)
        deployment_id = params.pop("deployment_id", None)

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

    @overload
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
        **params,
    ):
        ...

    @overload
    @classmethod
    async def atranscribe_raw(
        cls,
        *,
        deployment_id=None,
        file=None,
        filename=None,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        **params,
    ):
        ...

    @classmethod
    async def atranscribe_raw(
        cls,
        *args,
        **params,
    ):
        if len(args) > 8:
            raise TypeError(
                f"atranscribe_raw() takes from 4 to 9 positional arguments but {len(args)+1} were given"
            )
        util.check_required(*args, method_name="atranscribe_raw", required=["model", "file", "filename"], **params)

        positional = list(args)
        model =  positional.pop(0) if positional else params.pop("model", None)
        file = positional.pop(0) if positional else params.pop("file", None)
        filename = positional.pop(0) if positional else params.pop("filename", None)
        api_key = positional.pop(0) if positional else params.pop("api_key", None)
        api_base = positional.pop(0) if positional else params.pop("api_base", None)
        api_type = positional.pop(0) if positional else params.pop("api_type", None)
        api_version = positional.pop(0) if positional else params.pop("api_version", None)
        organization = positional.pop(0) if positional else params.pop("organization", None)
        deployment_id = params.pop("deployment_id", None)

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

    @overload
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
        **params,
    ):
        ...

    @overload
    @classmethod
    async def atranslate_raw(
        cls,
        *,
        deployment_id=None,
        file=None,
        filename=None,
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
        organization=None,
        **params,
    ):
        ...

    @classmethod
    async def atranslate_raw(
        cls,
        *args,
        **params,
    ):
        if len(args) > 8:
            raise TypeError(
                f"atranslate_raw() takes from 4 to 9 positional arguments but {len(args)+1} were given"
            )
        util.check_required(*args, method_name="atranslate_raw", required=["model", "file", "filename"], **params)

        positional = list(args)
        model =  positional.pop(0) if positional else params.pop("model", None)
        file = positional.pop(0) if positional else params.pop("file", None)
        filename = positional.pop(0) if positional else params.pop("filename", None)
        api_key = positional.pop(0) if positional else params.pop("api_key", None)
        api_base = positional.pop(0) if positional else params.pop("api_base", None)
        api_type = positional.pop(0) if positional else params.pop("api_type", None)
        api_version = positional.pop(0) if positional else params.pop("api_version", None)
        organization = positional.pop(0) if positional else params.pop("organization", None)
        deployment_id = params.pop("deployment_id", None)

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
