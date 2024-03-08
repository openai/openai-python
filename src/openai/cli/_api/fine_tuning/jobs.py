from __future__ import annotations

from typing import TYPE_CHECKING
from argparse import ArgumentParser

if TYPE_CHECKING:
    from argparse import _SubParsersAction


def register(subparser: _SubParsersAction[ArgumentParser]) -> None:
    sub = subparser.add_parser("fine_tuning.jobs.create")
    sub = subparser.add_parser("fine_tuning.jobs.retrieve")
    sub = subparser.add_parser("fine_tuning.jobs.list")
    sub = subparser.add_parser("fine_tuning.jobs.cancel")
    sub = subparser.add_parser("fine_tuning.jobs.list_events")

class CLIFineTuningJobs:
    pass