#!/usr/bin/env -S python
from __future__ import annotations

import argparse
import io
from typing import Optional

import rich

from openai import OpenAI


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload a PDF and stream a response that references it using the Responses API.",
    )
    parser.add_argument("pdf_path", help="Path to a local PDF file")
    parser.add_argument(
        "--prompt",
        default="Summarize this document.",
        help="Instruction for the model",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-2024-08-06",
        help="Model name to use",
    )
    args = parser.parse_args()

    client = OpenAI()

    with open(args.pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Ensure the upload has a filename so the server infers application/pdf
    buf = io.BytesIO(pdf_bytes)
    buf.name = "document.pdf"

    uploaded = client.files.create(file=buf, purpose="user_data")

    with client.responses.stream(
        model=args.model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": args.prompt},
                    {"type": "input_file", "file_id": uploaded.id},
                ],
            }
        ],
    ) as stream:
        for event in stream:
            # Match existing examples: print any output text deltas
            if "output_text" in event.type:
                rich.print(event)

        rich.print(stream.get_final_response())


if __name__ == "__main__":
    main()
