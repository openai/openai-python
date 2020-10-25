from __future__ import absolute_import, division, print_function

from openai import util
from openai.api_resources.abstract.api_resource import APIResource
from openai.six.moves.urllib.parse import quote_plus


class DeletableAPIResource(APIResource):
    @classmethod
    def _cls_delete(cls, sid, **params):
        url = "%s/%s" % (cls.class_url(), quote_plus(util.utf8(sid)))
        return cls._static_request("delete", url, **params)

    @util.class_method_variant("_cls_delete")
    def delete(self, **params):
        self.refresh_from(self.request("delete", self.instance_url(), params))
        return self
