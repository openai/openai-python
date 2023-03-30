import json
import os
from typing import cast, Optional, AnyStr

import openai
from openai import api_requestor, util, error
from openai._typedefs import FilesType, FileType
from openai.api_resources.abstract import DeletableAPIResource, ListableAPIResource
from openai.util import ApiType


class File(ListableAPIResource, DeletableAPIResource):
    OBJECT_NAME = "files"

    @classmethod
    def __prepare_file_create(
        cls,
        file: FileType,
        purpose: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        api_type: Optional[str] = None,
        api_version: Optional[str] = None,
        organization: Optional[str] = None,
        user_provided_filename: Optional[str] = None,
    ):
        requestor = api_requestor.APIRequestor(
            api_key,
            api_base=api_base or openai.api_base,
            api_type=api_type,
            api_version=api_version,
            organization=organization,
        )
        typed_api_type, api_version = cls._get_api_type_and_version(
            api_type, api_version
        )

        if typed_api_type in (ApiType.AZURE, ApiType.AZURE_AD):
            base = cls.class_url()
            url = "/%s%s?api-version=%s" % (cls.azure_api_prefix, base, api_version)
        elif typed_api_type == ApiType.OPEN_AI:
            url = cls.class_url()
        else:
            raise error.InvalidAPIType("Unsupported API type %s" % api_type)

        # Set the filename on 'purpose' and 'model' to None so they are
        # interpreted as form data.
        files: FilesType = [("purpose", (None, purpose))]
        if model is not None:
            files.append(("model", (None, model)))
        if user_provided_filename is not None:
            files.append(
                ("file", (user_provided_filename, file, "application/octet-stream"))
            )
        else:
            files.append(("file", ("file", file, "application/octet-stream")))

        return requestor, url, files

    @classmethod
    def create(
        cls,
        file: FileType,
        purpose: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        api_type: Optional[str] = None,
        api_version: Optional[str] = None,
        organization: Optional[str] = None,
        user_provided_filename: Optional[str] = None,
    ):
        requestor, url, files = cls.__prepare_file_create(
            file,
            purpose,
            model,
            api_key,
            api_base,
            api_type,
            api_version,
            organization,
            user_provided_filename,
        )
        response, _, api_key = requestor.request("post", url, files=files)
        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )

    @classmethod
    async def acreate(
        cls,
        file: FileType,
        purpose: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        api_type: Optional[str] = None,
        api_version: Optional[str] = None,
        organization: Optional[str] = None,
        user_provided_filename: Optional[str] = None,
    ):
        requestor, url, files = cls.__prepare_file_create(
            file,
            purpose,
            model,
            api_key,
            api_base,
            api_type,
            api_version,
            organization,
            user_provided_filename,
        )
        response, _, api_key = await requestor.arequest("post", url, files=files)
        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )

    @classmethod
    def __prepare_file_download(
        cls,
        id: str,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        api_type: Optional[str] = None,
        api_version: Optional[str] = None,
        organization: Optional[str] = None,
    ):
        requestor = api_requestor.APIRequestor(
            api_key,
            api_base=api_base or openai.api_base,
            api_type=api_type,
            api_version=api_version,
            organization=organization,
        )
        typed_api_type, api_version = cls._get_api_type_and_version(
            api_type, api_version
        )

        if typed_api_type in (ApiType.AZURE, ApiType.AZURE_AD):
            base = cls.class_url()
            url = f"/{cls.azure_api_prefix}{base}/{id}/content?api-version={api_version}"
        elif typed_api_type == ApiType.OPEN_AI:
            url = f"{cls.class_url()}/{id}/content"
        else:
            raise error.InvalidAPIType("Unsupported API type %s" % api_type)

        return requestor, url

    @classmethod
    def download(
        cls,
        id: str,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        api_type: Optional[str] = None,
        api_version: Optional[str] = None,
        organization: Optional[str] = None,
    ):
        requestor, url = cls.__prepare_file_download(
            id, api_key, api_base, api_type, api_version, organization
        )

        result = requestor.request_raw("get", url)
        if not 200 <= result.status_code < 300:
            raise requestor.handle_error_response(
                result.content,
                result.status_code,
                json.loads(cast(bytes, result.content)),
                result.headers,
                stream_error=False,
            )
        return result.content

    @classmethod
    async def adownload(
        cls,
        id: str,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        api_type: Optional[str] = None,
        api_version: Optional[str] = None,
        organization: Optional[str] = None,
    ):
        requestor, url = cls.__prepare_file_download(
            id, api_key, api_base, api_type, api_version, organization
        )

        async with api_requestor.aiohttp_session() as session:
            result = await requestor.arequest_raw("get", url, session)
            if not 200 <= result.status < 300:
                raise requestor.handle_error_response(
                    result.content,
                    result.status,
                    json.loads(cast(bytes, result.content)),
                    result.headers,
                    stream_error=False,
                )
            return result.content

    @classmethod
    def __find_matching_files(cls, name: AnyStr, bytes: int, all_files, purpose):
        matching_files = []
        basename = os.path.basename(name)
        for f in all_files:
            if f["purpose"] != purpose:
                continue
            file_basename = os.path.basename(f["filename"])
            if file_basename != basename:
                continue
            if "bytes" in f and f["bytes"] != bytes:
                continue
            if "size" in f and int(f["size"]) != bytes:
                continue
            matching_files.append(f)
        return matching_files

    @classmethod
    def find_matching_files(
        cls,
        name: str,
        bytes: int,
        purpose: str,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        api_type: Optional[str] = None,
        api_version: Optional[str] = None,
        organization: Optional[str] = None,
    ):
        """Find already uploaded files with the same name, size, and purpose."""
        all_files = cls.list(
            api_key=api_key,
            api_base=api_base or openai.api_base,
            api_type=api_type,
            api_version=api_version,
            organization=organization,
        ).get("data", [])
        return cls.__find_matching_files(name, bytes, all_files, purpose)

    @classmethod
    async def afind_matching_files(
        cls,
        name: str,
        bytes: int,
        purpose: str,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        api_type: Optional[str] = None,
        api_version: Optional[str] = None,
        organization: Optional[str] = None,
    ):
        """Find already uploaded files with the same name, size, and purpose."""
        all_files = (
            await cls.alist(
                api_key=api_key,
                api_base=api_base or openai.api_base,
                api_type=api_type,
                api_version=api_version,
                organization=organization,
            )
        ).get("data", [])
        return cls.__find_matching_files(name, bytes, all_files, purpose)
