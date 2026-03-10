"""Chat fine-tuning commands for OpenAI CLI."""
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
    """Register chat fine-tuning subcommands."""
    sub = subparser.add_parser("chat.fine_tune", help="Chat fine-tuning operations")
    sub._action_groups.pop()
    
    sub_subparsers = sub.add_subparsers(dest="chat_ft_command")
    
    # Fine-tune a chat model
    create_parser = sub_subparsers.add_parser("create", help="Create a chat fine-tuning job")
    create_parser.add_argument("--training-file", required=True, help="Training file ID (JSONL format)")
    create_parser.add_argument("--model", default="gpt-3.5-turbo", help="Base model to fine-tune")
    create_parser.add_argument("--suffix", help="Custom suffix for model name")
    create_parser.add_argument("--epochs", type=int, default=3, help="Number of epochs")
    create_parser.set_defaults(func=_create_chat_ft)
    
    # List chat fine-tuning jobs
    list_parser = sub_subparsers.add_parser("list", help="List chat fine-tuning jobs")
    list_parser.add_argument("--limit", type=int, default=10, help="Max jobs to return")
    list_parser.set_defaults(func=_list_chat_ft)


class ChatFTCreateArgs(BaseModel):
    training_file: str
    model: str = "gpt-3.5-turbo"
    suffix: str | None = None
    epochs: int | None = None


class ChatFTListArgs(BaseModel):
    limit: int = 10


def _create_chat_ft(args: ChatFTCreateArgs) -> None:
    """Create a chat fine-tuning job."""
    client = get_client()
    
    params = {
        "model": args.model,
        "training_file": args.training_file,
    }
    
    if args.suffix:
        params["suffix"] = args.suffix
    if args.epochs:
        params["hyperparameters"] = {"n_epochs": args.epochs}
    
    job = client.fine_tuning.jobs.create(**params)
    
    print(f"✅ Chat fine-tuning job created: {job.id}")
    print(f"   Model: {job.model}")
    print(f"   Status: {job.status}")
    print(f"\n💡 To check status: openai chat.fine_tune get {job.id}")


def _list_chat_ft(args: ChatFTListArgs) -> None:
    """List chat fine-tuning jobs."""
    client = get_client()
    jobs = client.fine_tuning.jobs.list(limit=args.limit)
    
    print(f"{'ID':<50} {'Model':<25} {'Status':<15} {'Trained Tokens'}")
    print("-" * 100)
    
    for job in jobs.data:
        tokens = job.trained_tokens or 0
        print(f"{job.id:<50} {job.model:<25} {job.status:<15} {tokens}")
