from __future__ import absolute_import, division, print_function

import json
import os

import openai
from openai import api_requestor, util
from openai.api_resources.abstract import (
    DeletableAPIResource,
    ListableAPIResource,
)


class File(ListableAPIResource, DeletableAPIResource):
    OBJECT_NAME = "file"

    @classmethod
    def create(
        cls, api_key=None, api_base=None, api_version=None, organization=None, **params
    ):
        requestor = api_requestor.APIRequestor(
            api_key,
            api_base=api_base or openai.file_api_base or openai.api_base,
            api_version=api_version,
            organization=organization,
        )
        url = cls.class_url()
        supplied_headers = {"Content-Type": "multipart/form-data"}
        response, _, api_key = requestor.request(
            "post", url, params=params, headers=supplied_headers
        )
        return util.convert_to_openai_object(
            response, api_key, api_version, organization
        )

    @classmethod
    def download(
        cls, id, api_key=None, api_base=None, api_version=None, organization=None
    ):
        requestor = api_requestor.APIRequestor(
            api_key,
            api_base=api_base or openai.file_api_base or openai.api_base,
            api_version=api_version,
            organization=organization,
        )
        url = f"{cls.class_url()}/{id}/content"
        rbody, rcode, rheaders, _, _ = requestor.request_raw("get", url)
        if not 200 <= rcode < 300:
            raise requestor.handle_error_response(
                rbody, rcode, json.loads(rbody), rheaders, stream_error=False
            )
        return rbody

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
            api_base=api_base or openai.file_api_base or openai.api_base,
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
