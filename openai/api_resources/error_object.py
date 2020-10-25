from __future__ import absolute_import, division, print_function

from openai.util import merge_dicts
from openai.openai_object import OpenAIObject


class ErrorObject(OpenAIObject):
    def refresh_from(
        self,
        values,
        api_key=None,
        partial=False,
        api_version=None,
        organization=None,
        last_response=None,
    ):
        # Unlike most other API resources, the API will omit attributes in
        # error objects when they have a null value. We manually set default
        # values here to facilitate generic error handling.
        values = merge_dicts({"message": None, "type": None}, values)
        return super(ErrorObject, self).refresh_from(
            values, api_key, partial, api_version, organization, last_response
        )
