import json
import os
from typing import cast

import openai
from openai import api_requestor, util
from openai.api_resources.abstract import DeletableAPIResource, ListableAPIResource


class File(ListableAPIResource, DeletableAPIResource):
    OBJECT_NAME = "file"

    @classmethod
    def create(
        cls,
        file,
        purpose,
        model=None,
        api_key=None,
        api_base=None,
        api_version=None,
        organization=None,
    ):
        if purpose != "search" and model is not None:
            raise ValueError("'model' is only meaningful if 'purpose' is 'search'")
        requestor = api_requestor.APIRequestor(
            api_key,
            api_base=api_base or openai.api_base,
            api_version=api_version,
            organization=organization,
        )
        url = cls.class_url()
        # Set the filename on 'purpose' and 'model' to None so they are
        # interpreted as form data.
        files = [("file", file), ("purpose", (None, purpose))]
        if model is not None:
            files.append(("model", (None, model)))
        response, _, api_key = requestor.request("post", url, files=files)
        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )

    @classmethod
    def download(
        cls, id, api_key=None, api_base=None, api_version=None, organization=None
    ):
        requestor = api_requestor.APIRequestor(
            api_key,
            api_base=api_base or openai.api_base,
            api_version=api_version,
            organization=organization,
        )
        url = f"{cls.class_url()}/{id}/content"
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
    def find_matching_files(
        cls,
        api_key=None,
        api_base=None,
        api_version=None,
        organization=None,
        file=None,
        purpose=None,
    ):
        if file is None:
            raise openai.error.InvalidRequestError(
                "'file' is a required property", "file"
            )
        if purpose is None:
            raise openai.error.InvalidRequestError(
                "'purpose' is a required property", "purpose"
            )
        all_files = cls.list(
            api_key=api_key,
            api_base=api_base or openai.api_base,
            api_version=api_version,
            organization=organization,
        ).get("data", [])
        matching_files = []
        for f in all_files:
            if f["purpose"] != purpose:
                continue
            if not hasattr(file, "name") or f["filename"] != file.name:
                continue
            file.seek(0, os.SEEK_END)
            if f["bytes"] != file.tell():
                file.seek(0)
                continue
            file.seek(0)
            matching_files.append(f)
        return matching_files
