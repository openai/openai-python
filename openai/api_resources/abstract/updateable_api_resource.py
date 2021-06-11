from urllib.parse import quote_plus

from openai import util
from openai.api_resources.abstract.api_resource import APIResource


class UpdateableAPIResource(APIResource):
    @classmethod
    def modify(cls, sid, **params):
        url = "%s/%s" % (cls.class_url(), quote_plus(sid))
        return cls._static_request("post", url, **params)

    def save(self, idempotency_key=None, request_id=None):
        updated_params = self.serialize(None)
        headers = util.populate_headers(idempotency_key, request_id)

        if updated_params:
            self.refresh_from(
                self.request("post", self.instance_url(), updated_params, headers)
            )
        else:
            util.logger.debug("Trying to save already saved object %r", self)
        return self
