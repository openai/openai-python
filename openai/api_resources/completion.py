import time

from openai import util
from openai.api_resources.abstract import DeletableAPIResource, ListableAPIResource
from openai.api_resources.abstract.engine_api_resource import EngineAPIResource
from openai.error import TryAgain


class Completion(EngineAPIResource, ListableAPIResource, DeletableAPIResource):
    engine_required = True
    OBJECT_NAME = "completion"

    @classmethod
    def create(cls, *args, timeout=None, **kwargs):
        start = time.time()
        while True:
            try:
                return super().create(*args, **kwargs)
            except TryAgain as e:
                if timeout is not None and time.time() > start + timeout:
                    raise

                util.log_info("Waiting for snapshot to warm up", error=e)
