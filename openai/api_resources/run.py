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


class Run(CreateableAPIResource, UpdateableAPIResource, ListableAPIResource):
    OBJECT_NAME = "run"
