from __future__ import absolute_import, division, print_function

import json
import os
import tempfile

import openai
from openai import api_requestor, util
from openai.api_resources.abstract import (
    APIResource,
    CreateableAPIResource,
    DeletableAPIResource,
    ListableAPIResource,
    UpdateableAPIResource,
)
from openai.util import log_info


class File(ListableAPIResource):
    OBJECT_NAME = "file"

    @classmethod
    def create(
        cls, api_key=None, api_base=None, api_version=None, organization=None, **params
    ):
        requestor = api_requestor.APIRequestor(
            api_key,
            api_base=openai.file_api_base or openai.api_base,
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
