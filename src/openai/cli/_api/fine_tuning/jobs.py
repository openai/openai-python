from __future__ import annotations

from typing import TYPE_CHECKING
from argparse import ArgumentParser

from ..._utils import get_client, print_model
from ..._models import BaseModel
from ....types.fine_tuning import (
    FineTuningJob,
)

if TYPE_CHECKING:
    from argparse import _SubParsersAction


def register(subparser: _SubParsersAction[ArgumentParser]) -> None:
    sub = subparser.add_parser("fine_tuning.jobs.create")

    sub = subparser.add_parser("fine_tuning.jobs.retrieve")
    sub.add_argument(
        "-i",
        "--id",
        help="The ID of the fine-tuning job to retrieve.",
        required=True,
    )
    sub.set_defaults(
        func=CLIFineTuningJobs.retrieve, args_model=CLIFineTuningJobsRetrieveArgs
    )

    sub = subparser.add_parser("fine_tuning.jobs.list")
    sub = subparser.add_parser("fine_tuning.jobs.cancel")
    sub = subparser.add_parser("fine_tuning.jobs.list_events")


class CLIFineTuningJobsRetrieveArgs(BaseModel):
    id: str

class CLIFineTuningJobs:
    @staticmethod
    def retrieve(args: CLIFineTuningJobsRetrieveArgs) -> None:
        fine_tuning_job: FineTuningJob = get_client().fine_tuning.jobs.retrieve(
            fine_tuning_job_id=args.id
        )
        print_model(fine_tuning_job)