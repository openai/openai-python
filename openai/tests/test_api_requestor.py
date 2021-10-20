import json

import requests
from pytest_mock import MockerFixture

from openai import Model


def test_requestor_sets_request_id(mocker: MockerFixture) -> None:
    # Fake out 'requests' and confirm that the X-Request-Id header is set.

    got_headers = {}

    def fake_request(self, *args, **kwargs):
        nonlocal got_headers
        got_headers = kwargs["headers"]
        r = requests.Response()
        r.status_code = 200
        r.headers["content-type"] = "application/json"
        r._content = json.dumps({}).encode("utf-8")
        return r

    mocker.patch("requests.sessions.Session.request", fake_request)
    fake_request_id = "1234"
    Model.retrieve("xxx", request_id=fake_request_id)  # arbitrary API resource
    got_request_id = got_headers.get("X-Request-Id")
    assert got_request_id == fake_request_id
