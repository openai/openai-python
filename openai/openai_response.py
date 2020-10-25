from __future__ import absolute_import, division, print_function

import json


class OpenAIResponse(object):
    def __init__(self, body, code, headers):
        self.body = body
        self.code = code
        self.headers = headers
        self.data = json.loads(body)

    @property
    def idempotency_key(self):
        try:
            return self.headers["idempotency-key"]
        except KeyError:
            return None

    @property
    def request_id(self):
        try:
            return self.headers["request-id"]
        except KeyError:
            return None
