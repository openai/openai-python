from __future__ import annotations

import sys
import argparse
from typing import TYPE_CHECKING, Any, Sequence
from typing_extensions import override

if TYPE_CHECKING:
    from argparse import Namespace

SHELLS = ("bash", "zsh", "tcsh")


class PrintCompletionAction(argparse.Action):
    """Print shell completion script and exit."""

    @override
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        _namespace: Namespace,
        values: str | Sequence[Any] | None,
        _option_string: str | None = None,
    ) -> None:
        try:
            import shtab
        except ImportError:
            sys.stderr.write(
                "Shell completion requires 'shtab'. Install with: pip install 'openai[completion]'\n"
            )
            sys.exit(1)

        if not isinstance(values, str):
            sys.stderr.write("Shell completion requires a shell name\n")
            sys.exit(1)

        sys.stdout.write(shtab.complete(parser, values))
        parser.exit(0)


def add_completion_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--completion",
        choices=SHELLS,
        action=PrintCompletionAction,
        help="Generate shell completion script for the specified shell",
    )


def handle_completion(parser: argparse.ArgumentParser, args: list[str]) -> None:
    if "--completion" not in args:
        return
    index = args.index("--completion")
    if index + 1 >= len(args):
        return
    shell = args[index + 1]
    parser.parse_args(["--completion", shell])
