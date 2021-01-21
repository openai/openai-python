from openai.api_resources.abstract.engine_api_resource import EngineAPIResource


class HigherLevel(EngineAPIResource):
    api_prefix = "higherlevel"

    def get_url(self, base):
        return "/%s/%s" % (self.api_prefix, base)

    def classification(self, **params):
        return self.request("post", self.get_url("classifications"), params)

    def answer(self, **params):
        return self.request("post", self.get_url("answers"), params)

    def retriever_file_set_search(self, **params):
        return self.request("post", self.get_url("retriever_file_set_search"), params)
