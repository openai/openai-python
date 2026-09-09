# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import json
from email import policy
from typing import cast
from email.parser import BytesParser
from email.message import EmailMessage

import httpx2

from openai import omit
from openai._files import to_httpx_files
from openai._multipart import encode_multipart

ENCODINGS = {"offer": ("application/sdp", False), "settings": ("application/json", True)}
OFFER = "v=0\r\ns=Unicode π\r\n"


def test_encoded_parts_preserve_json_and_text() -> None:
    settings = {"nested": {"future": [False, None, "π"]}}
    body, files, content, content_type = encode_multipart(
        {"offer": OFFER, "settings": {"old": True}}, {"settings": settings}, ENCODINGS
    )
    request = httpx2.Request("POST", "https://example.test", data=body, files=to_httpx_files(files), content=content)
    payload = request.read()
    message = BytesParser(_class=EmailMessage, policy=policy.default).parsebytes(
        ("Content-Type: " + request.headers["content-type"] + "\r\n\r\n").encode() + payload
    )
    assert content_type == "multipart/form-data"
    parts = list(message.iter_parts())
    assert len(parts) == 2
    named = {part.get_param("name", header="content-disposition"): part for part in parts}
    assert named["offer"].get_content_type() == "application/sdp"
    assert named["offer"].get_payload(decode=True) == OFFER.encode()
    assert named["settings"].get_content_type() == "application/json"
    assert json.loads(cast(bytes, named["settings"].get_payload(decode=True))) == settings
    assert all(part.get_filename() is None for part in parts)


def test_raw_alternative_omits_absent_settings() -> None:
    body, files, content, content_type = encode_multipart({"offer": OFFER, "settings": omit}, None, ENCODINGS, "offer")
    assert body is None and files is None
    assert content == OFFER.encode()
    assert content_type == "application/sdp"


def test_explicit_null_is_a_json_part_not_a_raw_alternative() -> None:
    _body, files, content, content_type = encode_multipart({"offer": OFFER, "settings": None}, None, ENCODINGS, "offer")
    assert content is None
    assert content_type == "multipart/form-data"
    assert dict(files or [])["settings"] == (None, b"null", "application/json")


def test_extra_body_does_not_get_dropped_by_raw_alternative() -> None:
    _body, files, content, content_type = encode_multipart(
        {"offer": OFFER}, {"settings": {"future": True}}, ENCODINGS, "offer"
    )
    assert files is not None
    assert content is None
    assert content_type == "multipart/form-data"


def test_omit_override_removes_field() -> None:
    _body, _files, content, _content_type = encode_multipart(
        {"offer": OFFER, "settings": {}}, {"settings": omit}, ENCODINGS, "offer"
    )
    assert content == OFFER.encode()
