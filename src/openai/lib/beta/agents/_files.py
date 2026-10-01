from __future__ import annotations

from os import PathLike, walk
from typing import TYPE_CHECKING, Mapping, Sequence
from asyncio import CancelledError
from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath
from dataclasses import field, dataclass

from ...._types import Omit, Headers, FileTypes
from ...._exceptions import OpenAIError
from ....types.beta.hosted_environment_file_param import HostedEnvironmentFileParam
from ....types.beta.agents.environments.environment_file import EnvironmentFile

if TYPE_CHECKING:
    from ...streaming.agents._streams import _RequestOptions
    from ....resources.beta.agents.environments.files import Files, AsyncFiles

_MAX_FILES = 50
_MAX_BYTES = 50 * 1024 * 1024


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
    if path.stat().st_size > _MAX_BYTES:
        raise ValueError("An agent file must not exceed 50 MiB")
    return path.resolve()


def _prepare_selection(
    files: Mapping[str, str | PathLike[str]], options: _RequestOptions, defaults: Headers
) -> list[tuple[str, Path]]:
    if len(files) > _MAX_FILES:
        raise ValueError("Initial agent files must not exceed 50 files")
    headers = {key.lower(): value for key, value in defaults.items()}
    headers.update({key.lower(): value for key, value in (options["extra_headers"] or {}).items()})
    if len(files) > 1 and "idempotency-key" in headers and not isinstance(headers["idempotency-key"], Omit):
        raise ValueError("One Idempotency-Key cannot be reused for multiple file uploads")
    selected: list[tuple[str, Path]] = []
    destinations: set[str] = set()
    size = 0
    for destination, source in files.items():
        destination = _destination(destination)
        if any(
            destination == prior or destination.startswith(prior + "/") or prior.startswith(destination + "/")
            for prior in destinations
        ):
            raise ValueError("Selected agent files contain duplicate or conflicting destinations")
        destinations.add(destination)
        local = _local_file(source)
        size += local.stat().st_size
        selected.append((destination, local))
    if size > _MAX_BYTES:
        raise ValueError("Initial agent files must not exceed 50 MiB in total")
    return selected


def _matches(parts: tuple[str, ...], pattern: tuple[str, ...]) -> bool:
    if not pattern:
        return not parts
    if pattern[0] == "**":
        return _matches(parts, pattern[1:]) or bool(parts) and _matches(parts[1:], pattern)
    return bool(parts) and fnmatchcase(parts[0], pattern[0]) and _matches(parts[1:], pattern[1:])


def directory_files(root: str | PathLike[str], destination: str, include: Sequence[str]) -> dict[str, Path]:
    directory = Path(root).absolute()
    if isinstance(include, str) or not include:
        raise ValueError("Select directory files with explicit include patterns")
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("The selected directory must be a directory, not a symlink")
    directory = directory.resolve()
    # System aliases such as macOS /tmp are allowed above the chosen root.
    _destination(destination + "/selected-file")
    patterns: list[tuple[str, ...]] = []
    for pattern in include:
        if not pattern or PurePosixPath(pattern).is_absolute() or ".." in PurePosixPath(pattern).parts:
            raise ValueError("Include patterns must stay inside the selected directory")
        patterns.append(PurePosixPath(pattern).parts)
    selected: dict[str, Path] = {}
    for current, directories, names in walk(directory, followlinks=False):
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
            if chosen and name not in directories:
                selected[str(PurePosixPath(destination) / relative.as_posix())] = source
    if not selected:
        raise ValueError("The include patterns did not select any files")
    return selected


def prepare(resource: Files, files: Mapping[str, str | PathLike[str]], options: _RequestOptions) -> PreparedAgentFiles:
    selected = _prepare_selection(files, options, resource._client.default_headers)
    prepared = PreparedAgentFiles()
    try:
        for destination, source in selected:
            uploaded = resource._client.files.create(file=source, purpose="user_data", **options)
            prepared.uploaded_file_ids.append(uploaded.id)
            prepared.files.append({"type": "file_id", "file_id": uploaded.id, "path": destination})
    except Exception as error:
        raise AgentFilePreparationError(prepared) from error
    return prepared


async def async_prepare(
    resource: AsyncFiles, files: Mapping[str, str | PathLike[str]], options: _RequestOptions
) -> PreparedAgentFiles:
    selected = _prepare_selection(files, options, resource._client.default_headers)
    prepared = PreparedAgentFiles()
    try:
        for destination, source in selected:
            uploaded = await resource._client.files.create(file=source, purpose="user_data", **options)
            prepared.uploaded_file_ids.append(uploaded.id)
            prepared.files.append({"type": "file_id", "file_id": uploaded.id, "path": destination})
    except CancelledError as error:
        error.__dict__["prepared"] = prepared
        raise
    except Exception as error:
        raise AgentFilePreparationError(prepared) from error
    return prepared


def _upload_file(file: FileTypes, path: str) -> str:
    destination = _destination(path)
    content = file[1] if isinstance(file, tuple) else file
    if isinstance(content, PathLike):
        _local_file(content)
    elif isinstance(content, bytes) and len(content) > _MAX_BYTES:
        raise ValueError("An agent file must not exceed 50 MiB")
    return destination


def upload(
    resource: Files, environment_id: str, file: FileTypes, path: str, options: _RequestOptions
) -> StagedAgentFile:
    destination = _upload_file(file, path)
    uploaded = resource._client.files.create(file=file, purpose="user_data", **options)
    try:
        staged = resource.create(environment_id, type="file_id", file_id=uploaded.id, path=destination, **options)
    except Exception as error:
        raise AgentFileStagingError(uploaded.id) from error
    return StagedAgentFile(uploaded_file_id=uploaded.id, file=staged)


async def async_upload(
    resource: AsyncFiles, environment_id: str, file: FileTypes, path: str, options: _RequestOptions
) -> StagedAgentFile:
    destination = _upload_file(file, path)
    uploaded = await resource._client.files.create(file=file, purpose="user_data", **options)
    try:
        staged = await resource.create(environment_id, type="file_id", file_id=uploaded.id, path=destination, **options)
    except CancelledError as error:
        error.__dict__["uploaded_file_id"] = uploaded.id
        raise
    except Exception as error:
        raise AgentFileStagingError(uploaded.id) from error
    return StagedAgentFile(uploaded_file_id=uploaded.id, file=staged)
