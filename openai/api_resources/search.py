from openai.api_resources.abstract.api_resource import APIResource


class Search(APIResource):
    @classmethod
    def class_url(cls):
        return "/search_indices/search"

    @classmethod
    def create_alpha(cls, **params):
        instance = cls()
        return instance.request("post", cls.class_url(), params)
