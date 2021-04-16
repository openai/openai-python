from openai.api_resources.abstract import (
    ListableAPIResource,
    DeletableAPIResource,
)
from openai import util


class CountTokens(ListableAPIResource, DeletableAPIResource):

    @classmethod
    def count_tokens(
        cls, api_key=None, api_base=None, api_version=None, organization=None, **params
    ):
        return util.check_tokens(
            params
        )
