# Custom tests for MIME handling of PDF uploads
from __future__ import annotations

import io
import json
import os
from datetime import datetime

import httpx
import pytest
from respx import MockRouter

from openai import OpenAI

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


@pytest.mark.respx(base_url=base_url)
@pytest.mark.parametrize("use_tuple", [True, False])
def test_files_create_pdf_sets_filename_and_mime(client: OpenAI, respx_mock: MockRouter, use_tuple: bool) -> None:
    """
    Ensure that when uploading PDF content we set a filename and the part content-type.

    - With tuple format (filename, bytes, content_type) we should see application/pdf explicitly.
    - With a named file-like object (.name) we should at least see a filename in the part; content-type may be generic.
    """
    # Prepare handler to assert multipart content
    def _assert_and_respond(request: httpx.Request) -> httpx.Response:  # type: ignore[override]
        body = request.content  # bytes of multipart form
        assert b"multipart/form-data" in request.headers.get("Content-Type", "").encode(), "request must be multipart"
        assert b"name=\"file\"" in body, "multipart must include 'file' part"
        assert b"filename=\"document.pdf\"" in body, "should include filename for server-side MIME sniffing"
        if use_tuple:
            # When tuple content type is passed, httpx should include application/pdf for that part
            assert b"Content-Type: application/pdf" in body, "expected part Content-Type application/pdf"
        return httpx.Response(
            200,
            json={
                "id": "file_123",
                "bytes": 123,
                "created_at": int(datetime.now().timestamp()),
                "filename": "document.pdf",
                "object": "file",
                "purpose": "user_data",
                "status": "uploaded",
            },
        )

    respx_mock.post("/files").mock(side_effect=_assert_and_respond)

    pdf_bytes = b"%PDF-1.4\n%... minimal pdf header ...\n"

    if use_tuple:
        file_value = ("document.pdf", pdf_bytes, "application/pdf")
    else:
        buf = io.BytesIO(pdf_bytes)
        buf.name = "document.pdf"  # type: ignore[attr-defined]
        file_value = buf

    file_obj = client.files.create(file=file_value, purpose="user_data")
    assert file_obj.id.startswith("file_")
    assert file_obj.filename == "document.pdf"
