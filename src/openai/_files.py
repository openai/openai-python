from __future__ import annotations

import io
import os
import pathlib
import mimetypes
from typing import overload
from typing_extensions import TypeGuard

import anyio

from ._types import (
    FileTypes,
    FileContent,
    RequestFiles,
    HttpxFileTypes,
    Base64FileInput,
    HttpxFileContent,
    HttpxRequestFiles,
)
from ._utils import is_tuple_t, is_mapping_t, is_sequence_t


def is_base64_file_input(obj: object) -> TypeGuard[Base64FileInput]:
    return isinstance(obj, io.IOBase) or isinstance(obj, os.PathLike)


def is_file_content(obj: object) -> TypeGuard[FileContent]:
    return (
        isinstance(obj, bytes) or isinstance(obj, tuple) or isinstance(obj, io.IOBase) or isinstance(obj, os.PathLike)
    )


def assert_is_file_content(obj: object, *, key: str | None = None) -> None:
    if not is_file_content(obj):
        prefix = f"Expected entry at `{key}`" if key is not None else f"Expected file input `{obj!r}`"
        raise RuntimeError(
            f"{prefix} to be bytes, an io.IOBase instance, PathLike or a tuple but received {type(obj)} instead. See https://github.com/openai/openai-python/tree/main#file-uploads"
        ) from None


def _guess_content_type_from_filename(filename: str | None) -> str | None:
    """Guess content type from filename using mimetypes module."""
    if not filename:
        return None
    guessed, _ = mimetypes.guess_type(filename)
    return guessed


def _sniff_content_type_from_bytes(data: bytes) -> str | None:
    """Minimal sniffing for common types we care about."""
    # PDF
    if data.startswith(b"%PDF-"):
        return "application/pdf"
    # PNG
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    # JPEG
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    # GIF
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return "image/gif"
    return None


def _ensure_tuple_with_content_type(
    filename: str | None, content: HttpxFileContent, inferred: str | None
) -> tuple[str | None, HttpxFileContent, str | None]:
    """Ensure we return a 3-tuple with content type if we inferred one."""
    if inferred:
        return (filename, content, inferred)
    return (filename, content, None)


@overload
def to_httpx_files(files: None) -> None: ...


@overload
def to_httpx_files(files: RequestFiles) -> HttpxRequestFiles: ...


def to_httpx_files(files: RequestFiles | None) -> HttpxRequestFiles | None:
    if files is None:
        return None

    if is_mapping_t(files):
        files = {key: _transform_file(file) for key, file in files.items()}
    elif is_sequence_t(files):
        files = [(key, _transform_file(file)) for key, file in files]
    else:
        raise TypeError(f"Unexpected file type input {type(files)}, expected mapping or sequence")

    return files


def _transform_file(file: FileTypes) -> HttpxFileTypes:
    if is_file_content(file):
        if isinstance(file, os.PathLike):
            path = pathlib.Path(file)
            data = path.read_bytes()
            filename = path.name
            inferred = _guess_content_type_from_filename(filename)
            return _ensure_tuple_with_content_type(filename, data, inferred)

        if isinstance(file, bytes):
            inferred = _sniff_content_type_from_bytes(file)
            return _ensure_tuple_with_content_type(None, file, inferred)

        if isinstance(file, io.IOBase):
            # Attempt to use file name if available
            filename = None
            try:
                name_attr = getattr(file, "name", None)
                if isinstance(name_attr, str):
                    filename = os.path.basename(name_attr)
            except Exception:
                pass
            
            data = file.read()
            inferred = _guess_content_type_from_filename(filename) or _sniff_content_type_from_bytes(data)
            return _ensure_tuple_with_content_type(filename, data, inferred)

        return file

    if is_tuple_t(file):
        return (file[0], read_file_content(file[1]), *file[2:])

    raise TypeError(f"Expected file types input to be a FileContent type or to be a tuple")


def read_file_content(file: FileContent) -> HttpxFileContent:
    if isinstance(file, os.PathLike):
        return pathlib.Path(file).read_bytes()
    return file


@overload
async def async_to_httpx_files(files: None) -> None: ...


@overload
async def async_to_httpx_files(files: RequestFiles) -> HttpxRequestFiles: ...


async def async_to_httpx_files(files: RequestFiles | None) -> HttpxRequestFiles | None:
    if files is None:
        return None

    if is_mapping_t(files):
        files = {key: await _async_transform_file(file) for key, file in files.items()}
    elif is_sequence_t(files):
        files = [(key, await _async_transform_file(file)) for key, file in files]
    else:
        raise TypeError("Unexpected file type input {type(files)}, expected mapping or sequence")

    return files


async def _async_transform_file(file: FileTypes) -> HttpxFileTypes:
    if is_file_content(file):
        if isinstance(file, os.PathLike):
            path = anyio.Path(file)
            data: bytes = await path.read_bytes()
            filename = os.path.basename(str(file))
            inferred = _guess_content_type_from_filename(filename)
            return _ensure_tuple_with_content_type(filename, data, inferred)

        if isinstance(file, bytes):
            inferred = _sniff_content_type_from_bytes(file)
            return _ensure_tuple_with_content_type(None, file, inferred)

        if isinstance(file, io.IOBase):
            # Attempt to use file name if available
            filename = None
            try:
                name_attr = getattr(file, "name", None)
                if isinstance(name_attr, str):
                    filename = os.path.basename(name_attr)
            except Exception:
                pass
            
            data = file.read()
            inferred = _guess_content_type_from_filename(filename) or _sniff_content_type_from_bytes(data)
            return _ensure_tuple_with_content_type(filename, data, inferred)

        return file

    if is_tuple_t(file):
        return (file[0], await async_read_file_content(file[1]), *file[2:])

    raise TypeError(f"Expected file types input to be a FileContent type or to be a tuple")


async def async_read_file_content(file: FileContent) -> HttpxFileContent:
    if isinstance(file, os.PathLike):
        return await anyio.Path(file).read_bytes()

    return file
