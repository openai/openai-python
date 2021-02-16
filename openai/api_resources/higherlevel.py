from openai.api_resources.abstract.engine_api_resource import EngineAPIResource


class HigherLevel(EngineAPIResource):
    api_prefix = "higherlevel"

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

    @classmethod
    def file_set_search(cls, **params):
        instance = cls()
        return instance.request("post", cls.get_url("file_set_search"), params)
