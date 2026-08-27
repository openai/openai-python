from __future__ import annotations

import time
from typing import TYPE_CHECKING

from ..types.file_object import FileObject

if TYPE_CHECKING:
    from ..resources.files import Files, AsyncFiles


def wait_for_file_processing(
    files: Files,
    id: str,
    *,
    poll_interval: float,
    max_wait_seconds: float,
) -> FileObject:
    """Poll a file using the caller's resource and sleep hooks."""
    TERMINAL_STATES = {"processed", "error", "deleted"}

    start = time.time()
    file = files.retrieve(id)
    while file.status not in TERMINAL_STATES:
        files._sleep(poll_interval)

        file = files.retrieve(id)
        if time.time() - start > max_wait_seconds:
            raise RuntimeError(
                f"Giving up on waiting for file {id} to finish processing after {max_wait_seconds} seconds."
            )

    return file


async def async_wait_for_file_processing(
    files: AsyncFiles,
    id: str,
    *,
    poll_interval: float,
    max_wait_seconds: float,
) -> FileObject:
    """Poll a file using the caller's async resource and sleep hooks."""
    TERMINAL_STATES = {"processed", "error", "deleted"}

    start = time.time()
    file = await files.retrieve(id)
    while file.status not in TERMINAL_STATES:
        await files._sleep(poll_interval)

        file = await files.retrieve(id)
        if time.time() - start > max_wait_seconds:
            raise RuntimeError(
                f"Giving up on waiting for file {id} to finish processing after {max_wait_seconds} seconds."
            )

    return file
