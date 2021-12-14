from openai.openai_object import OpenAIObject


class Answer(OpenAIObject):
    @classmethod
    def get_url(self):
        return "/answers"

    @classmethod
    def create(cls, **params):
        instance = cls()
        return instance.request("post", cls.get_url(), params)
