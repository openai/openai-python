import sys
from pathlib import Path

import rich

from openai import OpenAI

# generate this file using `./generate_file.sh`
file = Path("/tmp/big_test_file.txt")

client = OpenAI()


def from_disk() -> None:
    print("uploading file from disk")

    upload = client.uploads.upload_file_chunked(
        file=file,
        mime_type="txt",
        purpose="batch",
    )
    rich.print(upload)


def from_in_memory() -> None:
    print("uploading file from memory")

    # read the data into memory ourselves to simulate
    # it coming from somewhere else
    data = file.read_bytes()
    filename = "my_file.txt"

    upload = client.uploads.upload_file_chunked(
        file=data,
        filename=filename,
        bytes=len(data),
        mime_type="txt",
        purpose="batch",
    )
    rich.print(upload)


if "memory" in sys.argv:
    from_in_memory()
else:
    from_disk()
