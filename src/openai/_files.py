from __future__ import annotations

import io
import os
import pathlib
import mimetypes
import asyncio
from typing import Optional, overload
from typing_extensions import TypeGuard

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
    if is_tuple_t(file):
        name = file[0]
        content = read_file_content(file[1])

        if len(file) >= 3 and file[2] is not None:
            if len(file) >= 4:
                return (name, content, file[2], file[3])
            return (name, content, file[2])

        inferred: Optional[str] = _guess_content_type_from_filename(name)
        if inferred is None:
            if isinstance(content, (bytes, bytearray)):
                inferred = _sniff_content_type_from_bytes(bytes(content)) or "application/octet-stream"
            elif isinstance(file[1], os.PathLike):
                try:
                    inferred = _guess_content_type_from_filename(pathlib.Path(file[1]).name)  # type: ignore[arg-type]
                except Exception:
                    inferred = None

        if len(file) >= 4:
            return (name, content, inferred, file[3])
        if inferred is not None:
            return (name, content, inferred)
        return (name, content)

    if is_file_content(file):
        if isinstance(file, os.PathLike):
            path = pathlib.Path(file)
            data = path.read_bytes()
            ctype = _guess_content_type_from_filename(path.name) or _sniff_content_type_from_bytes(data)
            if ctype is not None:
                return (path.name, data, ctype)
            return (path.name, data)

        elif isinstance(file, (bytes, bytearray)):
            data = bytes(file)
            ctype = _sniff_content_type_from_bytes(data) or "application/octet-stream"
            name = _default_filename_for_content_type(ctype)
            return (name, data, ctype)

        elif isinstance(file, io.IOBase):
            file_name = None
            try:
                name_attr = getattr(file, "name", None)
                if isinstance(name_attr, str):
                    file_name = os.path.basename(name_attr)
            except Exception:
                file_name = None

            ctype = _guess_content_type_from_filename(file_name)
            if ctype is not None:
                return (file_name, file, ctype)
            return (file_name, file)

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
    if is_tuple_t(file):
        name = file[0]
        content = await async_read_file_content(file[1])

        if len(file) >= 3 and file[2] is not None:
            if len(file) >= 4:
                return (name, content, file[2], file[3])
            return (name, content, file[2])

        inferred: Optional[str] = _guess_content_type_from_filename(name)
        if inferred is None:
            if isinstance(content, (bytes, bytearray)):
                inferred = _sniff_content_type_from_bytes(bytes(content)) or "application/octet-stream"
            elif isinstance(file[1], os.PathLike):
                try:
                    inferred = _guess_content_type_from_filename(pathlib.Path(file[1]).name)  # type: ignore[arg-type]
                except Exception:
                    inferred = None

        if len(file) >= 4:
            return (name, content, inferred, file[3])
        if inferred is not None:
            return (name, content, inferred)
        return (name, content)
    
    if is_file_content(file):
        if isinstance(file, os.PathLike):
            name = os.path.basename(os.fspath(file))
            data = await asyncio.to_thread(lambda: pathlib.Path(file).read_bytes())
            ctype = _guess_content_type_from_filename(name) or _sniff_content_type_from_bytes(data)
            if ctype is not None:
                return (name, data, ctype)
            return (name, data)

        elif isinstance(file, (bytes, bytearray)):
            data = bytes(file)
            ctype = _sniff_content_type_from_bytes(data) or "application/octet-stream"
            name = _default_filename_for_content_type(ctype)
            return (name, data, ctype)

        elif isinstance(file, io.IOBase):
            file_name = None
            try:
                name_attr = getattr(file, "name", None)
                if isinstance(name_attr, str):
                    file_name = os.path.basename(name_attr)
            except Exception:
                file_name = None

            ctype = _guess_content_type_from_filename(file_name)
            if ctype is not None:
                return (file_name, file, ctype)
            return (file_name, file)

    raise TypeError(f"Expected file types input to be a FileContent type or to be a tuple")


async def async_read_file_content(file: FileContent) -> HttpxFileContent:
    if isinstance(file, os.PathLike):
        return await asyncio.to_thread(lambda: pathlib.Path(file).read_bytes())

    return file


def _guess_content_type_from_filename(filename: Optional[str]) -> Optional[str]:
    if not filename:
        return None
    guessed, _ = mimetypes.guess_type(filename)
    return guessed


def _sniff_content_type_from_bytes(data: bytes) -> Optional[str]:
    # PDF: %PDF-
    if len(data) >= 4 and data[:4] == b"%PDF":
        return "application/pdf"
    # PNG: 89 50 4E 47 0D 0A 1A 0A
    if len(data) >= 8 and data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    # JPEG: FF D8 FF
    if len(data) >= 3 and data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    # GIF: GIF87a or GIF89a
    if len(data) >= 6 and (data[:6] == b"GIF87a" or data[:6] == b"GIF89a"):
        return "image/gif"
    return None


def _default_filename_for_content_type(content_type: str) -> str:
    if content_type == "application/pdf":
        return "upload.pdf"
    if content_type == "image/png":
        return "upload.png"
    if content_type == "image/jpeg":
        return "upload.jpg"
    if content_type == "image/gif":
        return "upload.gif"
    return "upload.bin"
