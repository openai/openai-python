from __future__ import annotations

from typing import TYPE_CHECKING
from argparse import ArgumentParser

from . import migrate

if TYPE_CHECKING:
    from argparse import _SubParsersAction


def register_commands(subparser: _SubParsersAction[ArgumentParser]) -> None:
    migrate.register(subparser)
