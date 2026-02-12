from __future__ import annotations

from typing import TYPE_CHECKING
from argparse import ArgumentParser

from . import completions
from . import fine_tune

if TYPE_CHECKING:
    from argparse import _SubParsersAction


def register(subparser: _SubParsersAction[ArgumentParser]) -> None:
    completions.register(subparser)
    fine_tune.register(subparser)
