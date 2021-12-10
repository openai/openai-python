from openai.openai_object import OpenAIObject


class Classification(OpenAIObject):
    @classmethod
    def get_url(self):
        return "/classifications"

    @classmethod
    def create(cls, **params):
        instance = cls()
        return instance.request("post", cls.get_url(), params)
