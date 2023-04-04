from openai.openai_object import OpenAIObject


class Customer(OpenAIObject):
    @classmethod
    def get_url(cls, customer, endpoint):
        url = f"/customer/{customer}/{endpoint}"
        return url

    @classmethod
    def create(cls, customer, endpoint, **params):
        url = cls.get_url(customer, endpoint)
        instance = cls()
        return instance.request("post", url, params)

    @classmethod
    def acreate(cls, customer, endpoint, **params):
        url = cls.get_url(customer, endpoint)
        instance = cls()
        return instance.arequest("post", url, params)
