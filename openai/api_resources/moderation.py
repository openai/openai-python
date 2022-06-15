from typing import List, Optional, Union

from openai.openai_object import OpenAIObject


class Moderation(OpenAIObject):
    VALID_MODEL_NAMES: List[str] = ["text-moderation-stable", "text-moderation-latest"]

    @classmethod
    def get_url(self):
        return "/moderations"

    @classmethod
    def create(cls, input: Union[str, List[str]], model: Optional[str] = None):
        if model not in cls.VALID_MODEL_NAMES:
            raise ValueError(
                f"The parameter model should be chosen from {cls.VALID_MODEL_NAMES} "
                f"and it is default to be None."
            )

        instance = cls()
        return instance.request("post", cls.get_url(), {"input": input, "model": model})
