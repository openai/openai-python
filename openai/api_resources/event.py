from __future__ import absolute_import, division, print_function

import json
import os
import tempfile

from openai import util
from openai.api_resources.abstract import (
    APIResource,
    CreateableAPIResource,
    DeletableAPIResource,
    ListableAPIResource,
    UpdateableAPIResource,
)
from openai.openai_object import OpenAIObject
from openai.six.moves.urllib.parse import quote_plus
from openai.util import log_info


class Event(ListableAPIResource):
    OBJECT_NAME = "event"

    @classmethod
    def list(cls, stream=False, **params):
        if stream:
            return cls._events_stream(**params)
        return super().list(**params)

    @classmethod
    def _events_stream(cls, **params):
        while True:
            resp = cls.list(**params)
            for item in resp.data:
                yield item
            if not resp.has_more:
                return
            elif len(resp.data) > 0:
                params["offset"] = resp.data[-1].data.created_by.lineno + 1
            if params.get("limit") is None:
                params["limit"] = 100
            if params.get("timeout") is None:
                params["timeout"] = 10
