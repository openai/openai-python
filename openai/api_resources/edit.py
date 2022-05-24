import time

from openai import util
from openai.api_resources.abstract.engine_api_resource import EngineAPIResource
from openai.error import InvalidRequestError, TryAgain


class Edit(EngineAPIResource):
    engine_required = False
    OBJECT_NAME = "edits"

    @classmethod
    def create(cls, *args, **kwargs):
        """
        Creates a new edit for the provided input, instruction, and parameters.
        """
        start = time.time()
        timeout = kwargs.pop("timeout", None)
        if kwargs.get("model", None) is None and kwargs.get("engine", None) is None:
            raise InvalidRequestError(
                "Must provide an 'engine' or 'model' parameter to create an Edit.",
                param="engine",
            )

        while True:
            try:
                return super().create(*args, **kwargs)
            except TryAgain as e:
                if timeout is not None and time.time() > start + timeout:
                    raise

                util.log_info("Waiting for model to warm up", error=e)
