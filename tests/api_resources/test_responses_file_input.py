from __future__ import annotations

import io
import os

import httpx
import pytest
from respx import MockRouter

from openai import OpenAI

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


@pytest.mark.respx(base_url=base_url)
def test_responses_stream_with_input_file(client: OpenAI, respx_mock: MockRouter) -> None:
    # mock file upload
    respx_mock.post("/files").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "file_abc",
                "bytes": 10,
                "created_at": 0,
                "filename": "document.pdf",
                "object": "file",
                "purpose": "user_data",
                "status": "uploaded",
            },
        )
    )

    # mock responses stream, simplified: return a single final response payload
    respx_mock.post("/responses").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "resp_123",
                "object": "response",
                "status": "in_progress",
                "output": [
                    {"id": "out_1", "type": "output_text", "text": "Summary"}
                ],
                "metadata": None,
                "incomplete_details": None,
                "usage": None,
                "response": None,
            },
        )
    )

    client = client  # OpenAI fixture

    buf = io.BytesIO(b"%PDF-1.4\n...")
    buf.name = "document.pdf"  # type: ignore[attr-defined]

    uploaded = client.files.create(file=buf, purpose="user_data")

    with client.responses.stream(
        model="gpt-4o-2024-08-06",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Summarize this document."},
                    {"type": "input_file", "file_id": uploaded.id},
                ],
            }
        ],
    ) as stream:
        # Iterate to trigger consumption
        for _ in stream:
            pass
        final = stream.get_final_response()
        assert final is not None
