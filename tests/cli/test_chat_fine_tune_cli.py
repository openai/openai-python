from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from openai._types import omit
from openai.cli import _cli
from openai.cli._errors import CLIError
from openai.cli._api.chat import fine_tune


def test_chat_fine_tune_list_command_is_registered() -> None:
    parser = _cli._build_parser()
    parsed = parser.parse_args(["api", "chat.fine_tune.list"])

    assert parsed.func == fine_tune.CLIChatFineTune.list


def test_chat_fine_tune_create_requires_training_file() -> None:
    parser = _cli._build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["api", "chat.fine_tune.create", "--model", "gpt-4o-mini"])


def test_chat_fine_tune_create_calls_fine_tuning_jobs_create(monkeypatch: pytest.MonkeyPatch) -> None:
    client = MagicMock()
    created_job = MagicMock()
    client.fine_tuning.jobs.create.return_value = created_job
    printed: list[object] = []

    monkeypatch.setattr(fine_tune, "get_client", lambda: client)
    monkeypatch.setattr(fine_tune, "print_model", lambda model: printed.append(model))

    args = fine_tune.CLIChatFineTuneCreateArgs(
        model="gpt-4o-mini",
        training_file="file-123",
        hyperparameters='{"n_epochs": 2}',
    )
    fine_tune.CLIChatFineTune.create(args)

    client.fine_tuning.jobs.create.assert_called_once_with(
        model="gpt-4o-mini",
        training_file="file-123",
        hyperparameters={"n_epochs": 2},
        suffix=omit,
        validation_file=omit,
    )
    assert printed == [created_job]


def test_chat_fine_tune_list_calls_fine_tuning_jobs_list(monkeypatch: pytest.MonkeyPatch) -> None:
    client = MagicMock()
    listed_jobs = MagicMock()
    client.fine_tuning.jobs.list.return_value = listed_jobs
    printed: list[object] = []

    monkeypatch.setattr(fine_tune, "get_client", lambda: client)
    monkeypatch.setattr(fine_tune, "print_model", lambda model: printed.append(model))

    args = fine_tune.CLIChatFineTuneListArgs()
    fine_tune.CLIChatFineTune.list(args)

    client.fine_tuning.jobs.list.assert_called_once_with(after=omit, limit=omit)
    assert printed == [listed_jobs]


def test_chat_fine_tune_apply_aliases_to_resume(monkeypatch: pytest.MonkeyPatch) -> None:
    client = MagicMock()
    resumed_job = MagicMock()
    client.fine_tuning.jobs.resume.return_value = resumed_job
    printed: list[object] = []

    monkeypatch.setattr(fine_tune, "get_client", lambda: client)
    monkeypatch.setattr(fine_tune, "print_model", lambda model: printed.append(model))

    fine_tune.CLIChatFineTune.apply(fine_tune.CLIChatFineTuneApplyArgs(id="ftjob-123"))

    client.fine_tuning.jobs.resume.assert_called_once_with(fine_tuning_job_id="ftjob-123")
    assert printed == [resumed_job]


def test_cli_main_returns_error_code_when_chat_fine_tune_handler_raises(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(_cli.sys, "argv", ["openai", "api", "chat.fine_tune.list"])

    def raise_error(_: object) -> None:
        raise CLIError("boom")

    monkeypatch.setattr(fine_tune.CLIChatFineTune, "list", staticmethod(raise_error))

    exit_code = _cli.main()
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Error:" in captured.err
    assert "boom" in captured.err
