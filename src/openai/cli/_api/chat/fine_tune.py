from __future__ import annotations

import json
from typing import TYPE_CHECKING
from argparse import ArgumentParser

from ..._models import BaseModel
from ..._utils import get_client, print_model
from ...._types import Omittable, omit
from ...._utils import is_given
from ....pagination import SyncCursorPage
from ....types.fine_tuning import FineTuningJob

if TYPE_CHECKING:
    from argparse import _SubParsersAction


def register(subparser: _SubParsersAction[ArgumentParser]) -> None:
    sub = subparser.add_parser("chat.fine_tune.create")
    sub.add_argument(
        "-m",
        "--model",
        help="The chat model to fine-tune.",
        required=True,
    )
    sub.add_argument(
        "-F",
        "--training-file",
        help="The training file to fine-tune the model on.",
        required=True,
    )
    sub.add_argument(
        "-H",
        "--hyperparameters",
        help="JSON string of hyperparameters to use for fine-tuning.",
        type=str,
    )
    sub.add_argument(
        "-s",
        "--suffix",
        help="A suffix to add to the fine-tuned model name.",
    )
    sub.add_argument(
        "-V",
        "--validation-file",
        help="The validation file to use for fine-tuning.",
    )
    sub.set_defaults(func=CLIChatFineTune.create, args_model=CLIChatFineTuneCreateArgs)

    sub = subparser.add_parser("chat.fine_tune.list")
    sub.add_argument(
        "-a",
        "--after",
        help="Identifier for the last job from the previous pagination request.",
    )
    sub.add_argument(
        "-l",
        "--limit",
        help="Number of chat fine-tuning jobs to retrieve.",
        type=int,
    )
    sub.set_defaults(func=CLIChatFineTune.list, args_model=CLIChatFineTuneListArgs)

    sub = subparser.add_parser("chat.fine_tune.apply")
    sub.add_argument(
        "-i",
        "--id",
        help="The ID of the chat fine-tuning job to apply.",
        required=True,
    )
    sub.set_defaults(func=CLIChatFineTune.apply, args_model=CLIChatFineTuneApplyArgs)


class CLIChatFineTuneCreateArgs(BaseModel):
    model: str
    training_file: str
    hyperparameters: Omittable[str] = omit
    suffix: Omittable[str] = omit
    validation_file: Omittable[str] = omit


class CLIChatFineTuneListArgs(BaseModel):
    after: Omittable[str] = omit
    limit: Omittable[int] = omit


class CLIChatFineTuneApplyArgs(BaseModel):
    id: str


class CLIChatFineTune:
    @staticmethod
    def create(args: CLIChatFineTuneCreateArgs) -> None:
        hyperparameters = json.loads(str(args.hyperparameters)) if is_given(args.hyperparameters) else omit
        fine_tuning_job: FineTuningJob = get_client().fine_tuning.jobs.create(
            model=args.model,
            training_file=args.training_file,
            hyperparameters=hyperparameters,
            suffix=args.suffix,
            validation_file=args.validation_file,
        )
        print_model(fine_tuning_job)

    @staticmethod
    def list(args: CLIChatFineTuneListArgs) -> None:
        fine_tuning_jobs: SyncCursorPage[FineTuningJob] = get_client().fine_tuning.jobs.list(
            after=args.after or omit,
            limit=args.limit or omit,
        )
        print_model(fine_tuning_jobs)

    @staticmethod
    def apply(args: CLIChatFineTuneApplyArgs) -> None:
        # `apply` is a CLI convenience alias to the existing resume operation.
        fine_tuning_job: FineTuningJob = get_client().fine_tuning.jobs.resume(fine_tuning_job_id=args.id)
        print_model(fine_tuning_job)
