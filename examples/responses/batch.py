#!/usr/bin/env -S rye run python
import json
import tempfile
import time
from pathlib import Path

from openai import OpenAI


client = OpenAI()


def write_batch_input(path: Path) -> None:
    requests = [
        {
            "custom_id": "request-1",
            "method": "POST",
            "url": "/v1/responses",
            "body": {
                "model": "gpt-5.2",
                "input": "Write one sentence about the Batch API.",
                "max_output_tokens": 100,
            },
        },
        {
            "custom_id": "request-2",
            "method": "POST",
            "url": "/v1/responses",
            "body": {
                "model": "gpt-5.2",
                "input": "Write one sentence about Python SDKs.",
                "max_output_tokens": 100,
            },
        },
    ]

    with path.open("w") as file:
        for request in requests:
            file.write(json.dumps(request) + "\n")


with tempfile.TemporaryDirectory() as tmpdir:
    batch_input_path = Path(tmpdir) / "batch_input.jsonl"
    write_batch_input(batch_input_path)

    batch_input_file = client.files.create(
        file=batch_input_path,
        purpose="batch",
    )

    batch = client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/responses",
        completion_window="24h",
    )

    print(f"Batch created: {batch.id}")

    while batch.status not in {"completed", "failed", "expired", "cancelled"}:
        time.sleep(30)
        batch = client.batches.retrieve(batch.id)
        print(f"Batch status: {batch.status}")

    print(f"Batch finished with status: {batch.status}")

    if batch.output_file_id:
        output = client.files.content(batch.output_file_id).read().decode("utf-8")
        print("Batch output:")
        print(output)

    if batch.error_file_id:
        errors = client.files.content(batch.error_file_id).read().decode("utf-8")
        print("Batch errors:")
        print(errors)
