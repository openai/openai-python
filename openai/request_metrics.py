from __future__ import absolute_import, division, print_function


class RequestMetrics(object):
    def __init__(self, request_id, request_duration_ms):
        self.request_id = request_id
        self.request_duration_ms = request_duration_ms

    def payload(self):
        return {
            "request_id": self.request_id,
            "request_duration_ms": self.request_duration_ms,
        }
