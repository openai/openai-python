from __future__ import annotations

from pathlib import Path

import pytest

from openai.cli._tools import migrate
from openai.cli._errors import CLIError


def test_install_explains_how_to_migrate_on_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(migrate.sys, "platform", "win32")

    with pytest.raises(CLIError) as exc_info:
        migrate.install()

    message = str(exc_info.value)
    assert "run `openai migrate` from WSL" in message
    assert "do not need to install `grit` or add it to PATH" in message


def test_migrate_invokes_downloaded_grit_without_requiring_path(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str | Path]] = []

    monkeypatch.setattr(migrate, "install", lambda: Path("/tmp/grit"))
    monkeypatch.setattr(migrate.subprocess, "check_call", calls.append)

    migrate.migrate(migrate.MigrateArgs(unknown_args=["--force"]))

    assert calls == [[Path("/tmp/grit"), "apply", "openai", "--force"]]
