from __future__ import annotations

import json
from typing import TYPE_CHECKING
from argparse import ArgumentParser

from ..._utils import get_client, print_model
from ...._types import Omittable, omit
from ...._utils import is_given
from ..._models import BaseModel
from ....pagination import SyncCursorPage
from ....types.fine_tuning import (
    FineTuningJob,
    FineTuningJobEvent,
)

if TYPE_CHECKING:
    from argparse import _SubParsersAction


def register(subparser: _SubParsersAction[ArgumentParser]) -> None:
    sub = subparser.add_parser("chat_fine_tunes.create")
    sub.add_argument(
        "-m",
        "--model",
        help="The model to fine-tune.",
        required=True,
    )
    sub.add_argument(
        "-t",
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
        "-v",
        "--validation-file",
        help="The validation file to use for fine-tuning.",
    )
    sub.set_defaults(func=CLIChatFineTunes.create, args_model=CLIChatFineTunesCreateArgs)

    sub = subparser.add_parser("chat_fine_tunes.get")
    sub.add_argument(
        "-i",
        "--id",
        help="The ID of the fine-tuning job to retrieve.",
        required=True,
    )
    sub.set_defaults(func=CLIChatFineTunes.retrieve, args_model=CLIChatFineTunesRetrieveArgs)

    sub = subparser.add_parser("chat_fine_tunes.list")
    sub.add_argument(
        "-a",
        "--after",
        help="Identifier for the last job from the previous pagination request. If provided, only jobs created after this job will be returned.",
    )
    sub.add_argument(
        "-l",
        "--limit",
        help="Number of fine-tuning jobs to retrieve.",
        type=int,
    )
    sub.set_defaults(func=CLIChatFineTunes.list, args_model=CLIChatFineTunesListArgs)

    sub = subparser.add_parser("chat_fine_tunes.cancel")
    sub.add_argument(
        "-i",
        "--id",
        help="The ID of the fine-tuning job to cancel.",
        required=True,
    )
    sub.set_defaults(func=CLIChatFineTunes.cancel, args_model=CLIChatFineTunesCancelArgs)


class CLIChatFineTunesCreateArgs(BaseModel):
    model: str
    training_file: str
    hyperparameters: Omittable[str] = omit
    suffix: Omittable[str] = omit
    validation_file: Omittable[str] = omit


class CLIChatFineTunesRetrieveArgs(BaseModel):
    id: str


class CLIChatFineTunesListArgs(BaseModel):
    after: Omittable[str] = omit
    limit: Omittable[int] = omit


class CLIChatFineTunesCancelArgs(BaseModel):
    id: str


class CLIChatFineTunes:
    @staticmethod
    def create(args: CLIChatFineTunesCreateArgs) -> None:
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
    def retrieve(args: CLIChatFineTunesRetrieveArgs) -> None:
        fine_tuning_job: FineTuningJob = get_client().fine_tuning.jobs.retrieve(fine_tuning_job_id=args.id)
        print_model(fine_tuning_job)

    @staticmethod
    def list(args: CLIChatFineTunesListArgs) -> None:
        fine_tuning_jobs: SyncCursorPage[FineTuningJob] = get_client().fine_tuning.jobs.list(
            after=args.after or omit, limit=args.limit or omit
        )
        print_model(fine_tuning_jobs)

    @staticmethod
    def cancel(args: CLIChatFineTunesCancelArgs) -> None:
        fine_tuning_job: FineTuningJob = get_client().fine_tuning.jobs.cancel(fine_tuning_job_id=args.id)
        print_model(fine_tuning_job)