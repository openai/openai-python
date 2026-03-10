"""Fine-tuning commands for OpenAI CLI."""
from __future__ import annotations

import sys
import json
from typing import TYPE_CHECKING
from argparse import ArgumentParser

from ..._utils import get_client
from ..._models import BaseModel

if TYPE_CHECKING:
    from argparse import _SubParsersAction


def register(subparser: _SubParsersAction[ArgumentParser]) -> None:
    """Register fine-tuning subcommands."""
    sub = subparser.add_parser("fine_tune", help="Fine-tuning operations")
    sub._action_groups.pop()
    
    sub_subparsers = sub.add_subparsers(dest="fine_tune_command")
    
    # List fine-tuning jobs
    list_parser = sub_subparsers.add_parser("list", help="List fine-tuning jobs")
    list_parser.add_argument("--limit", type=int, default=10, help="Max jobs to return")
    list_parser.set_defaults(func=_list_jobs)
    
    # Create fine-tuning job
    create_parser = sub_subparsers.add_parser("create", help="Create a fine-tuning job")
    create_parser.add_argument("--training-file", required=True, help="Training file ID")
    create_parser.add_argument("--model", required=True, help="Base model to fine-tune")
    create_parser.add_argument("--suffix", help="Custom suffix for model name")
    create_parser.add_argument("--epochs", type=int, default=3, help="Number of epochs")
    create_parser.add_argument("--batch-size", type=int, help="Batch size")
    create_parser.add_argument("--learning-rate", type=float, help="Learning rate multiplier")
    create_parser.set_defaults(func=_create_job)
    
    # Get fine-tuning job status
    get_parser = sub_subparsers.add_parser("get", help="Get fine-tuning job status")
    get_parser.add_argument("job_id", help="Fine-tuning job ID")
    get_parser.set_defaults(func=_get_job)
    
    # Cancel fine-tuning job
    cancel_parser = sub_subparsers.add_parser("cancel", help="Cancel a fine-tuning job")
    cancel_parser.add_argument("job_id", help="Fine-tuning job ID")
    cancel_parser.set_defaults(func=_cancel_job)


class FineTuneListArgs(BaseModel):
    limit: int = 10


class FineTuneCreateArgs(BaseModel):
    training_file: str
    model: str
    suffix: str | None = None
    epochs: int | None = None
    batch_size: int | None = None
    learning_rate_multiplier: float | None = None


class FineTuneGetArgs(BaseModel):
    job_id: str


class FineTuneCancelArgs(BaseModel):
    job_id: str


def _list_jobs(args: FineTuneListArgs) -> None:
    """List fine-tuning jobs."""
    client = get_client()
    jobs = client.fine_tuning.jobs.list(limit=args.limit)
    
    print(f"{'ID':<50} {'Model':<30} {'Status':<15} {'Created'}")
    print("-" * 120)
    
    for job in jobs.data:
        created = job.created_at.strftime("%Y-%m-%d %H:%M") if job.created_at else "N/A"
        print(f"{job.id:<50} {job.model:<30} {job.status:<15} {created}")


def _create_job(args: FineTuneCreateArgs) -> None:
    """Create a fine-tuning job."""
    client = get_client()
    
    params = {
        "model": args.model,
        "training_file": args.training_file,
    }
    
    if args.suffix:
        params["suffix"] = args.suffix
    if args.epochs:
        params["hyperparameters"] = {"n_epochs": args.epochs}
    if args.batch_size:
        if "hyperparameters" not in params:
            params["hyperparameters"] = {}
        params["hyperparameters"]["batch_size"] = args.batch_size
    if args.learning_rate:
        if "hyperparameters" not in params:
            params["hyperparameters"] = {}
        params["hyperparameters"]["learning_rate_multiplier"] = args.learning_rate
    
    job = client.fine_tuning.jobs.create(**params)
    
    print(f"✅ Fine-tuning job created: {job.id}")
    print(f"   Model: {job.model}")
    print(f"   Status: {job.status}")


def _get_job(args: FineTuneGetArgs) -> None:
    """Get fine-tuning job status."""
    client = get_client()
    job = client.fine_tuning.jobs.retrieve(args.job_id)
    
    print(f"Fine-tuning Job: {job.id}")
    print(f"  Model: {job.model}")
    print(f"  Status: {job.status}")
    print(f"  Trained tokens: {job.trained_tokens or 0}")
    print(f"  Created: {job.created_at}")
    print(f"  Finished at: {job.finished_at}")
    
    if job.error:
        print(f"  Error: {job.error}")


def _cancel_job(args: FineTuneCancelArgs) -> None:
    """Cancel a fine-tuning job."""
    client = get_client()
    job = client.fine_tuning.jobs.cancel(args.job_id)
    print(f"✅ Fine-tuning job cancelled: {job.id}")
