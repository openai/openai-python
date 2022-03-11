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
        user_provided_filename=None,
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
        files = [("purpose", (None, purpose))]
        if model is not None:
            files.append(("model", (None, model)))
        if user_provided_filename is not None:
            files.append(("file", (user_provided_filename, file)))
        else:
            files.append(("file", file))
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
        name,
        bytes,
        purpose,
        api_key=None,
        api_base=None,
        api_version=None,
        organization=None,
    ):
        """Find already uploaded files with the same name, size, and purpose."""
        all_files = cls.list(
            api_key=api_key,
            api_base=api_base or openai.api_base,
            api_version=api_version,
            organization=organization,
        ).get("data", [])
        matching_files = []
        basename = os.path.basename(name)
        for f in all_files:
            if f["purpose"] != purpose:
                continue
            file_basename = os.path.basename(f["filename"])
            if file_basename != basename:
                continue
            if f["bytes"] != bytes:
                continue
            matching_files.append(f)
        return matching_files
