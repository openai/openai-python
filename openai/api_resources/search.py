import time

from openai import util
from openai.api_resources.abstract.engine_api_resource import EngineAPIResource
from openai.error import TryAgain


class Search(EngineAPIResource):
    OBJECT_NAME = "search"

    @classmethod
    def create(cls, *args, **kwargs):
        """
        Creates a new search for the provided input and parameters.

        See https://beta.openai.com/docs/api-reference/search for a list
        of valid parameters.
        """

        start = time.time()
        timeout = kwargs.pop("timeout", None)

        while True:
            try:
                return super().create(*args, **kwargs)
            except TryAgain as e:
                if timeout is not None and time.time() > start + timeout:
                    raise

                util.log_info("Waiting for model to warm up", error=e)
