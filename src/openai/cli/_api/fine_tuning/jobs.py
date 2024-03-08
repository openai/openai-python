from __future__ import annotations

from typing import TYPE_CHECKING
from argparse import ArgumentParser

from ..._utils import get_client, print_model
from ...._types import NOT_GIVEN, NotGivenOr
from ..._models import BaseModel
from ....pagination import SyncCursorPage
from ....types.fine_tuning import (
    FineTuningJob,
    FineTuningJobEvent,
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
    sub.set_defaults(func=CLIFineTuningJobs.list, args_model=CLIFineTuningJobsListArgs)

    sub = subparser.add_parser("fine_tuning.jobs.cancel")
    sub.add_argument(
        "-i",
        "--id",
        help="The ID of the fine-tuning job to cancel.",
        required=True,
    )
    sub.set_defaults(
        func=CLIFineTuningJobs.cancel, args_model=CLIFineTuningJobsCancelArgs
    )

    sub = subparser.add_parser("fine_tuning.jobs.list_events")
    sub.add_argument(
        "-i",
        "--id",
        help="The ID of the fine-tuning job to list events for.",
        required=True,
    )
    sub.add_argument(
        "-a",
        "--after",
        help="Identifier for the last event from the previous pagination request. If provided, only events created after this event will be returned.",
    )
    sub.add_argument(
        "-l",
        "--limit",
        help="Number of fine-tuning job events to retrieve.",
        type=int,
    )
    sub.set_defaults(
        func=CLIFineTuningJobs.list_events, args_model=CLIFineTuningJobsListEventsArgs
    )


class CLIFineTuningJobsRetrieveArgs(BaseModel):
    id: str

class CLIFineTuningJobsListArgs(BaseModel):
    after: NotGivenOr[str] = NOT_GIVEN
    limit: NotGivenOr[int] = NOT_GIVEN

class CLIFineTuningJobsCancelArgs(BaseModel):
    id: str

class CLIFineTuningJobsListEventsArgs(BaseModel):
    id: str
    after: NotGivenOr[str] = NOT_GIVEN
    limit: NotGivenOr[int] = NOT_GIVEN


class CLIFineTuningJobs:
    @staticmethod
    def retrieve(args: CLIFineTuningJobsRetrieveArgs) -> None:
        fine_tuning_job: FineTuningJob = get_client().fine_tuning.jobs.retrieve(
            fine_tuning_job_id=args.id
        )
        print_model(fine_tuning_job)
    
    @staticmethod
    def list(args: CLIFineTuningJobsListArgs) -> None:
        fine_tuning_jobs: SyncCursorPage[
            FineTuningJob
        ] = get_client().fine_tuning.jobs.list(
            after=args.after or NOT_GIVEN, limit=args.limit or NOT_GIVEN
        )
        print_model(fine_tuning_jobs)
    
    @staticmethod
    def cancel(args: CLIFineTuningJobsCancelArgs) -> None:
        fine_tuning_job: FineTuningJob = get_client().fine_tuning.jobs.cancel(
            fine_tuning_job_id=args.id
        )
        print_model(fine_tuning_job)
    
    @staticmethod
    def list_events(args: CLIFineTuningJobsListEventsArgs) -> None:
        fine_tuning_job_events: SyncCursorPage[
            FineTuningJobEvent
        ] = get_client().fine_tuning.jobs.list_events(
            fine_tuning_job_id=args.id,
            after=args.after or NOT_GIVEN,
            limit=args.limit or NOT_GIVEN,
        )
        print_model(fine_tuning_job_events)