from urllib.parse import quote_plus

from openai.api_resources.abstract.api_resource import APIResource


class DeletableAPIResource(APIResource):
    @classmethod
    def delete(cls, sid, **params):
        if isinstance(cls, APIResource):
            raise ValueError(".delete may only be called as a class method now.")
        url = "%s/%s" % (cls.class_url(), quote_plus(sid))
        return cls._static_request("delete", url, **params)
