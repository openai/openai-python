from __future__ import absolute_import, division, print_function

from openai import util


class VerifyMixin(object):
    def verify(self, idempotency_key=None, request_id=None, **params):
        url = self.instance_url() + "/verify"
        headers = util.populate_headers(idempotency_key, request_id)
        self.refresh_from(self.request("post", url, params, headers))
        return self
