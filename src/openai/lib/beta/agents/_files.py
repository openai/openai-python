from __future__ import annotations

from io import IOBase
from os import PathLike, walk, fstat
from stat import S_ISREG
from typing import TYPE_CHECKING, Mapping, BinaryIO, Sequence, Generator, cast
from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath
from contextlib import ExitStack, contextmanager
from dataclasses import field, dataclass
from typing_extensions import TypedDict, override

import httpx2
from anyio.to_thread import run_sync

from ...._types import Body, Omit, Query, Headers, NotGiven, FileTypes
from ...._exceptions import OpenAIError
from ....types.beta.hosted_environment_file_param import HostedEnvironmentFileParam
from ....types.beta.agents.environments.environment_file import EnvironmentFile

if TYPE_CHECKING:
    from ....resources.beta.agents.environments.files import Files, AsyncFiles


class _RequestOptions(TypedDict):
    extra_headers: Headers | None
    extra_query: Query | None
    extra_body: Body | None
    timeout: float | httpx2.Timeout | None | NotGiven


@dataclass(frozen=True)
class _SelectedFile(PathLike[str]):
    path: Path
    identity: tuple[int, int, int]

    @override
    def __fspath__(self) -> str:
        return str(self.path)


@dataclass
class PreparedAgentFiles:
    """Beta: file inputs and upload ownership for explicit Files API cleanup."""

    files: list[HostedEnvironmentFileParam] = field(default_factory=list[HostedEnvironmentFileParam])
    uploaded_file_ids: list[str] = field(default_factory=list[str])


@dataclass(frozen=True)
class StagedAgentFile:
    """Beta: a staged environment file and its separately owned Files API upload."""

    uploaded_file_id: str
    file: EnvironmentFile


class AgentFilePreparationError(OpenAIError):
    """Beta: preparation failed; successful uploads remain available for cleanup."""

    def __init__(self, prepared: PreparedAgentFiles) -> None:
        super().__init__("Could not prepare all agent files; successful uploads remain caller-owned")
        self.prepared = prepared


class AgentFileStagingError(OpenAIError):
    """Beta: staging failed after upload; the upload remains caller-owned."""

    def __init__(self, uploaded_file_id: str) -> None:
        super().__init__("Could not stage the agent file; the upload remains caller-owned")
        self.uploaded_file_id = uploaded_file_id


def _destination(value: str) -> str:
    components = value.split("/")[1:]
    if not value.startswith("/workspace/") or "\x00" in value or "\\" in value:
        raise ValueError("Agent file destinations must be absolute POSIX file paths under /workspace")
    if any(component in ("", ".", "..") for component in components):
        raise ValueError("Agent file destinations cannot contain empty, dot or parent components")
    if (
        components[1] in (".codex", ".managed-agents")
        or components[1].startswith(".managed-agents-")
        or value == "/workspace/outputs"
    ):
        raise ValueError("Agent file destination uses a reserved environment path")
    return value


def _local_file(value: str | PathLike[str]) -> Path:
    path = Path(value).absolute()
    if path.is_symlink():
        raise ValueError("Selected agent files must not be symlinks")
    if not path.is_file():
        raise ValueError("Selected agent files must be regular files")
    return path


def _prepare_selection(
    files: Mapping[str, str | PathLike[str]], options: _RequestOptions, defaults: Headers, stack: ExitStack
) -> list[tuple[str, Path, BinaryIO, int]]:
    headers = {key.lower(): value for key, value in defaults.items()}
    headers.update({key.lower(): value for key, value in (options["extra_headers"] or {}).items()})
    if len(files) > 1 and "idempotency-key" in headers and not isinstance(headers["idempotency-key"], Omit):
        raise ValueError("One Idempotency-Key cannot be reused for multiple file uploads")
    entries = list(files.items())
    destinations = {_destination(destination) for destination, _ in entries}
    for destination in destinations:
        if any(str(parent) in destinations for parent in PurePosixPath(destination).parents):
            raise ValueError("Selected agent files contain duplicate or conflicting destinations")
    selected: list[tuple[str, Path, BinaryIO, int]] = []
    for destination, source in entries:
        local = _local_file(source)
        handle, length = _open_local(local, stack, source.identity if isinstance(source, _SelectedFile) else None)
        selected.append((destination, local, handle, length))
    return selected


def _matches(parts: tuple[str, ...], pattern: tuple[str, ...], *, prefix: bool = False) -> bool:
    # A directory prefix is useful only if the pattern can select a descendant.
    if prefix and not parts:
        return bool(pattern)
    if not pattern:
        return not parts
    if pattern[0] == "**":
        return (
            _matches(parts, pattern[1:], prefix=prefix) or bool(parts) and _matches(parts[1:], pattern, prefix=prefix)
        )
    return bool(parts) and fnmatchcase(parts[0], pattern[0]) and _matches(parts[1:], pattern[1:], prefix=prefix)


def _walk_error(error: OSError) -> None:
    raise error


def directory_files(root: str | PathLike[str], destination: str, include: Sequence[str]) -> dict[str, PathLike[str]]:
    directory = Path(root).absolute()
    if isinstance(include, str) or not include:
        raise ValueError("Select directory files with explicit include patterns")
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("The selected directory must be a directory, not a symlink")
    directory = directory.resolve()
    # System aliases such as macOS /tmp are allowed above the chosen root.
    _destination(destination + "/a")  # Validate with the shortest possible filename.
    patterns: list[tuple[str, ...]] = []
    for pattern in include:
        if not pattern or PurePosixPath(pattern).is_absolute() or ".." in PurePosixPath(pattern).parts:
            raise ValueError("Include patterns must stay inside the selected directory")
        patterns.append(PurePosixPath(pattern).parts)
    selected: dict[str, PathLike[str]] = {}
    for current, directories, names in walk(directory, followlinks=False, onerror=_walk_error):
        if not Path(current).resolve().is_relative_to(directory):
            raise ValueError("Selected directory traversal left its root")
        directories.sort()
        for name in sorted([*directories, *names]):
            source = Path(current) / name
            relative = source.relative_to(directory)
            chosen = any(_matches(relative.parts, pattern) for pattern in patterns)
            if source.is_symlink():
                if chosen:
                    raise ValueError("Selected agent files must not be symlinks")
                if name in directories:
                    directories.remove(name)
                continue
            if name in directories:
                if not any(_matches(relative.parts, pattern, prefix=True) for pattern in patterns):
                    directories.remove(name)
                continue
            if chosen:
                canonical = source.resolve()
                if not canonical.is_relative_to(directory):
                    raise ValueError("Selected agent file is outside the chosen directory")
                metadata = canonical.lstat()
                selected[str(PurePosixPath(destination) / relative.as_posix())] = _SelectedFile(
                    canonical, (metadata.st_dev, metadata.st_ino, metadata.st_size)
                )
    if not selected:
        raise ValueError("The include patterns did not select any files")
    return selected


async def async_directory_files(
    root: str | PathLike[str], destination: str, include: Sequence[str]
) -> dict[str, PathLike[str]]:
    return await run_sync(directory_files, root, destination, include, abandon_on_cancel=True)


def _open_local(path: Path, stack: ExitStack, expected: tuple[int, int, int] | None = None) -> tuple[BinaryIO, int]:
    before = path.lstat()
    if not S_ISREG(before.st_mode):
        raise ValueError("Selected agent files must be regular files, not symlinks")
    if expected is not None and expected != (before.st_dev, before.st_ino, before.st_size):
        raise ValueError("Selected agent file changed after directory selection")
    handle = stack.enter_context(path.open("rb"))
    opened = fstat(handle.fileno())
    if (before.st_dev, before.st_ino, before.st_size) != (opened.st_dev, opened.st_ino, opened.st_size):
        raise ValueError("Selected agent file changed during preparation")
    return handle, opened.st_size


def _unchanged_size(handle: BinaryIO, length: int) -> None:
    if fstat(handle.fileno()).st_size != length:
        raise ValueError("Selected agent file changed during preparation")


def prepare(resource: Files, files: Mapping[str, str | PathLike[str]], options: _RequestOptions) -> PreparedAgentFiles:
    with ExitStack() as stack:
        selected = _prepare_selection(files, options, resource._client.default_headers, stack)
        prepared = PreparedAgentFiles()
        try:
            for destination, source, handle, length in selected:
                _unchanged_size(handle, length)
                uploaded = resource._client.files.create(file=(source.name, handle), purpose="user_data", **options)
                prepared.uploaded_file_ids.append(uploaded.id)
                prepared.files.append({"type": "file_id", "file_id": uploaded.id, "path": destination})
        except Exception as error:
            raise AgentFilePreparationError(prepared) from error
        except BaseException as error:
            error.__dict__["prepared"] = prepared
            raise
        return prepared


def _snapshot_selection(
    files: Mapping[str, str | PathLike[str]], options: _RequestOptions, defaults: Headers
) -> list[tuple[str, str, bytes]]:
    # The worker owns every handle it opens, even if its caller is cancelled.
    with ExitStack() as stack:
        selected = _prepare_selection(files, options, defaults, stack)
        return [
            (destination, source.name, _read_local(handle, length)) for destination, source, handle, length in selected
        ]


async def async_prepare(
    resource: AsyncFiles, files: Mapping[str, str | PathLike[str]], options: _RequestOptions
) -> PreparedAgentFiles:
    selected = await run_sync(
        _snapshot_selection, files, options, resource._client.default_headers, abandon_on_cancel=True
    )
    prepared = PreparedAgentFiles()
    try:
        for destination, filename, content in selected:
            uploaded = await resource._client.files.create(file=(filename, content), purpose="user_data", **options)
            prepared.uploaded_file_ids.append(uploaded.id)
            prepared.files.append({"type": "file_id", "file_id": uploaded.id, "path": destination})
    except Exception as error:
        raise AgentFilePreparationError(prepared) from error
    except BaseException as error:
        error.__dict__["prepared"] = prepared
        raise
    return prepared


def _read_local(handle: BinaryIO, length: int) -> bytes:
    _unchanged_size(handle, length)
    content = handle.read(length + 1)
    if len(content) != length:
        raise ValueError("Selected agent file changed during preparation")
    return content


def _snapshot_upload(file: FileTypes) -> FileTypes:
    with _upload_content(file) as opened:
        assert isinstance(opened, tuple) and isinstance(opened[1], IOBase)
        handle = cast(BinaryIO, opened[1])
        content = _read_local(handle, fstat(handle.fileno()).st_size)
        return cast(FileTypes, (opened[0], content, *opened[2:]))


@contextmanager
def _upload_content(file: FileTypes) -> Generator[FileTypes, None, None]:
    content = file[1] if isinstance(file, tuple) else file
    with ExitStack() as stack:
        if isinstance(content, PathLike):
            path = _local_file(content)
            handle, length = _open_local(path, stack)
            _unchanged_size(handle, length)
            yield cast(FileTypes, (file[0], handle, *file[2:])) if isinstance(file, tuple) else (path.name, handle)
            return
        yield file


def upload(
    resource: Files, environment_id: str, file: FileTypes, path: str, options: _RequestOptions
) -> StagedAgentFile:
    if not environment_id:
        raise ValueError("Expected a non-empty environment_id")
    destination = _destination(path)
    with _upload_content(file) as content:
        uploaded = resource._client.files.create(file=content, purpose="user_data", **options)
    try:
        staged = resource.create(environment_id, type="file_id", file_id=uploaded.id, path=destination, **options)
    except Exception as error:
        raise AgentFileStagingError(uploaded.id) from error
    except BaseException as error:
        error.__dict__["uploaded_file_id"] = uploaded.id
        raise
    return StagedAgentFile(uploaded_file_id=uploaded.id, file=staged)


async def async_upload(
    resource: AsyncFiles, environment_id: str, file: FileTypes, path: str, options: _RequestOptions
) -> StagedAgentFile:
    if not environment_id:
        raise ValueError("Expected a non-empty environment_id")
    destination = _destination(path)
    original = file[1] if isinstance(file, tuple) else file
    if isinstance(original, PathLike):
        file = await run_sync(_snapshot_upload, file, abandon_on_cancel=True)
    with _upload_content(file) as content:
        uploaded = await resource._client.files.create(file=content, purpose="user_data", **options)
    try:
        staged = await resource.create(environment_id, type="file_id", file_id=uploaded.id, path=destination, **options)
    except Exception as error:
        raise AgentFileStagingError(uploaded.id) from error
    except BaseException as error:
        error.__dict__["uploaded_file_id"] = uploaded.id
        raise
    return StagedAgentFile(uploaded_file_id=uploaded.id, file=staged)
