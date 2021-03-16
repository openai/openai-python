from openai.openai_object import OpenAIObject


class Classification(OpenAIObject):
    api_prefix = "v1"

    @classmethod
    def get_url(self, base):
        return "/%s/%s" % (self.api_prefix, base)

    @classmethod
    def create(cls, **params):
        instance = cls()
        return instance.request("post", cls.get_url("classifications"), params)
