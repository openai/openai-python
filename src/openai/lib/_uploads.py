"""Handwritten chunked-upload orchestration used by resource facades."""

from __future__ import annotations

import io
import os
import builtins
from typing import TYPE_CHECKING
from pathlib import Path

import anyio

from .._types import Omit, omit
from ..types.upload import Upload
from ..types.file_purpose import FilePurpose

if TYPE_CHECKING:
    from ..resources.uploads.uploads import Uploads, AsyncUploads


def upload_file_chunked(
    self: Uploads,
    *,
    file: os.PathLike[str] | bytes,
    mime_type: str,
    purpose: FilePurpose,
    filename: str | None = None,
    bytes: int | None = None,
    part_size: int | None = None,
    md5: str | Omit = omit,
) -> Upload:
    """Splits the given file into multiple parts and uploads them sequentially.

    ```py
    from pathlib import Path

    client.uploads.upload_file(
        file=Path("my-paper.pdf"),
        mime_type="pdf",
        purpose="assistants",
    )
    ```
    """
    # Keep the original module's mutable bindings and their lookup timing.
    # In particular, create() may change the default before the first read,
    # and parts.create() may replace the logger before each log call.
    from ..resources.uploads import uploads as resource_module

    if isinstance(file, builtins.bytes):
        if filename is None:
            raise TypeError("The `filename` argument must be given for in-memory files")

        if bytes is None:
            raise TypeError("The `bytes` argument must be given for in-memory files")
    else:
        if not isinstance(file, Path):
            file = Path(file)

        if not filename:
            filename = file.name

        if bytes is None:
            bytes = file.stat().st_size

    upload = self.create(
        bytes=bytes,
        filename=filename,
        mime_type=mime_type,
        purpose=purpose,
    )

    part_ids: list[str] = []

    if part_size is None:
        part_size = resource_module.DEFAULT_PART_SIZE

    if isinstance(file, builtins.bytes):
        buf: io.FileIO | io.BytesIO = io.BytesIO(file)
    else:
        buf = io.FileIO(file)

    try:
        while True:
            data = buf.read(part_size)
            if not data:
                # EOF
                break

            part = self.parts.create(upload_id=upload.id, data=data)
            resource_module.log.info("Uploaded part %s for upload %s", part.id, upload.id)
            part_ids.append(part.id)
    finally:
        buf.close()

    return self.complete(upload_id=upload.id, part_ids=part_ids, md5=md5)


async def async_upload_file_chunked(
    self: AsyncUploads,
    *,
    file: os.PathLike[str] | bytes,
    mime_type: str,
    purpose: FilePurpose,
    filename: str | None = None,
    bytes: int | None = None,
    part_size: int | None = None,
    md5: str | Omit = omit,
) -> Upload:
    """Splits the given file into multiple parts and uploads them sequentially.

    ```py
    from pathlib import Path

    client.uploads.upload_file(
        file=Path("my-paper.pdf"),
        mime_type="pdf",
        purpose="assistants",
    )
    ```
    """
    # Keep the original module's mutable bindings and their lookup timing.
    # In particular, create() may change the default before the first read,
    # and parts.create() may replace the logger before each log call.
    from ..resources.uploads import uploads as resource_module

    if isinstance(file, builtins.bytes):
        if filename is None:
            raise TypeError("The `filename` argument must be given for in-memory files")

        if bytes is None:
            raise TypeError("The `bytes` argument must be given for in-memory files")
    else:
        if not isinstance(file, anyio.Path):
            file = anyio.Path(file)

        if not filename:
            filename = file.name

        if bytes is None:
            stat = await file.stat()
            bytes = stat.st_size

    upload = await self.create(
        bytes=bytes,
        filename=filename,
        mime_type=mime_type,
        purpose=purpose,
    )

    part_ids: list[str] = []

    if part_size is None:
        part_size = resource_module.DEFAULT_PART_SIZE

    if isinstance(file, anyio.Path):
        fd = await file.open("rb")
        async with fd:
            while True:
                data = await fd.read(part_size)
                if not data:
                    # EOF
                    break

                part = await self.parts.create(upload_id=upload.id, data=data)
                resource_module.log.info("Uploaded part %s for upload %s", part.id, upload.id)
                part_ids.append(part.id)
    else:
        buf = io.BytesIO(file)

        try:
            while True:
                data = buf.read(part_size)
                if not data:
                    # EOF
                    break

                part = await self.parts.create(upload_id=upload.id, data=data)
                resource_module.log.info("Uploaded part %s for upload %s", part.id, upload.id)
                part_ids.append(part.id)
        finally:
            buf.close()

    return await self.complete(upload_id=upload.id, part_ids=part_ids, md5=md5)
