from openai.api_resources.abstract.api_resource import APIResource


class Search(APIResource):
    api_prefix = "v1"
    OBJECT_NAME = "search_indices"

    @classmethod
    def class_url(cls):
        return "/%s/%s" % (cls.api_prefix, cls.OBJECT_NAME)

    @classmethod
    def create_alpha(cls, **params):
        instance = cls()
        return instance.request("post", f"{cls.class_url()}/search", params)
