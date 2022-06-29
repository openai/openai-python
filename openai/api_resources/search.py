import time

from openai import util
from openai.api_resources.abstract.engine_api_resource import EngineAPIResource
from openai.error import InvalidRequestError, TryAgain


class Search(EngineAPIResource):
    engine_required = False
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
        api_type = kwargs.pop("api_type", None)
        typed_api_type = cls._get_api_type_and_version(api_type=api_type)[0]
        if typed_api_type in (util.ApiType.AZURE, util.ApiType.AZURE_AD):
            if kwargs.get("deployment_id", None) is None and kwargs.get("engine", None) is None:
                raise InvalidRequestError(
                    "Must provide an 'engine' or 'deployment_id' parameter to create a Search.",
                    param="engine",
                )
        else:
            if kwargs.get("model", None) is None and kwargs.get("engine", None) is None:
                raise InvalidRequestError(
                    "Must provide an 'engine' or 'model' parameter to create a Search.",
                    param="engine",
                )

        while True:
            try:
                return super().create(*args, **kwargs)
            except TryAgain as e:
                if timeout is not None and time.time() > start + timeout:
                    raise

                util.log_info("Waiting for model to warm up", error=e)
