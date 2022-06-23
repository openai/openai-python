import time
import warnings

from openai import util
from openai.api_resources.abstract import ListableAPIResource, UpdateableAPIResource
from openai.error import InvalidAPIType, TryAgain
from openai.util import ApiType


class Engine(ListableAPIResource, UpdateableAPIResource):
    OBJECT_NAME = "engines"

    def generate(self, timeout=None, **params):
        start = time.time()
        while True:
            try:
                return self.request(
                    "post",
                    self.instance_url() + "/generate",
                    params,
                    stream=params.get("stream"),
                    plain_old_data=True,
                )
            except TryAgain as e:
                if timeout is not None and time.time() > start + timeout:
                    raise

                util.log_info("Waiting for model to warm up", error=e)

    def search(self, **params):
        if self.typed_api_type in (ApiType.AZURE, ApiType.AZURE_AD):
            return self.request("post", self.instance_url("search"), params)
        elif self.typed_api_type == ApiType.OPEN_AI:
            return self.request("post", self.instance_url() + "/search", params)
        else:
            raise InvalidAPIType("Unsupported API type %s" % self.api_type)

    def embeddings(self, **params):
        warnings.warn(
            "Engine.embeddings is deprecated, use Embedding.create", DeprecationWarning
        )
        return self.request("post", self.instance_url() + "/embeddings", params)
