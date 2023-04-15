import base64
import time
from typing import Optional, Union, List

from openai import util
from openai.api_resources.abstract.engine_api_resource import EngineAPIResource
from openai.datalib.numpy_helper import assert_has_numpy
from openai.datalib.numpy_helper import numpy as np
from openai.error import TryAgain


class Embedding(EngineAPIResource):
    OBJECT_NAME = "embeddings"

    @classmethod
    def create(
        cls,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        api_type: Optional[str] = None,
        request_id: Optional[str] = None,
        api_version: Optional[str] = None,
        organization: Optional[str] = None,
        timeout: Optional[float] = None,
        model: Optional[str] = None,
        input: Optional[Union[str, List[str]]] = None,
        encoding_format: str = "base64",
        **params,
    ):
        """
        Creates a new embedding for the provided input and parameters.

        See https://platform.openai.com/docs/api-reference/embeddings for a list
        of valid parameters.
        """
        start = time.time()

        while True:
            try:
                response = super().create(
                    api_key=api_key,
                    api_base=api_base,
                    api_type=api_type,
                    api_version=api_version,
                    request_id=request_id,
                    organization=organization,
                    model=model,
                    input=input,
                    **params,
                )

                # If a user specifies base64, we'll just return the encoded string.
                # This is only for the default case.
                if not encoding_format:
                    for data in response.data:

                        # If an engine isn't using this optimization, don't do anything
                        if type(data["embedding"]) == str:
                            assert_has_numpy()
                            data["embedding"] = np.frombuffer(
                                base64.b64decode(data["embedding"]), dtype="float32"
                            ).tolist()

                return response
            except TryAgain as e:
                if timeout is not None and time.time() > start + timeout:
                    raise

                util.log_info("Waiting for model to warm up", error=e)

    @classmethod
    async def acreate(
        cls,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        api_type: Optional[str] = None,
        request_id: Optional[str] = None,
        api_version: Optional[str] = None,
        organization: Optional[str] = None,
        timeout: Optional[float] = None,
        model: Optional[str] = None,
        input: Optional[Union[str, List[str]]] = None,
        encoding_format: str = "base64",
        **params,
    ):
        """
        Creates a new embedding for the provided input and parameters.

        See https://platform.openai.com/docs/api-reference/embeddings for a list
        of valid parameters.
        """
        start = time.time()

        while True:
            try:
                response = await super().acreate(
                    api_key=api_key,
                    api_base=api_base,
                    api_type=api_type,
                    api_version=api_version,
                    request_id=request_id,
                    organization=organization,
                    model=model,
                    input=input,
                    **params,
                )

                # If a user specifies base64, we'll just return the encoded string.
                # This is only for the default case.
                if not encoding_format:
                    for data in response.data:

                        # If an engine isn't using this optimization, don't do anything
                        if type(data["embedding"]) == str:
                            data["embedding"] = np.frombuffer(
                                base64.b64decode(data["embedding"]), dtype="float32"
                            ).tolist()

                return response
            except TryAgain as e:
                if timeout is not None and time.time() > start + timeout:
                    raise

                util.log_info("Waiting for model to warm up", error=e)
