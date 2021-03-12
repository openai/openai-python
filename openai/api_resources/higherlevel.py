from openai.api_resources.abstract.engine_api_resource import EngineAPIResource


class HigherLevel(EngineAPIResource):
    api_prefix = "v1"

    @classmethod
    def get_url(self, base):
        return "/%s/%s" % (self.api_prefix, base)

    @classmethod
    def classification(cls, **params):
        instance = cls()
        return instance.request("post", cls.get_url("classifications"), params)

    @classmethod
    def answer(cls, **params):
        instance = cls()
        return instance.request("post", cls.get_url("answers"), params)
