from openai.api_resources.abstract.engine_api_resource import EngineAPIResource


class HigherLevel(EngineAPIResource):
    api_prefix = "higherlevel"

    def get_url(self, base):
        return "/%s/%ss" % (self.api_prefix, base)

    def classification(self, **params):
        return self.request("post", self.get_url("classification"), params)

    def answer(self, **params):
        return self.request("post", self.get_url("answer"), params)
