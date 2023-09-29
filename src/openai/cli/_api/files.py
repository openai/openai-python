from __future__ import annotations

from typing import TYPE_CHECKING
from argparse import ArgumentParser

from .._utils import get_client, print_model
from .._models import BaseModel
from .._progress import BufferReader

if TYPE_CHECKING:
    from argparse import _SubParsersAction


def register(subparser: _SubParsersAction[ArgumentParser]) -> None:
    sub = subparser.add_parser("files.create")

    sub.add_argument(
        "-f",
        "--file",
        required=True,
        help="File to upload",
    )
    sub.add_argument(
        "-p",
        "--purpose",
        help="Why are you uploading this file? (see https://platform.openai.com/docs/api-reference/ for purposes)",
        required=True,
    )
    sub.set_defaults(func=File.create, args_model=FileCreateArgs)

    sub = subparser.add_parser("files.retrieve")
    sub.add_argument("-i", "--id", required=True, help="The files ID")
    sub.set_defaults(func=File.get, args_model=FileCreateArgs)

    sub = subparser.add_parser("files.delete")
    sub.add_argument("-i", "--id", required=True, help="The files ID")
    sub.set_defaults(func=File.delete, args_model=FileCreateArgs)

    sub = subparser.add_parser("files.list")
    sub.set_defaults(func=File.list)


class FileIDArgs(BaseModel):
    id: str


class FileCreateArgs(BaseModel):
    file: str
    purpose: str


class File:
    @staticmethod
    def create(args: FileCreateArgs) -> None:
        with open(args.file, "rb") as file_reader:
            buffer_reader = BufferReader(file_reader.read(), desc="Upload progress")

        file = get_client().files.create(file=(args.file, buffer_reader), purpose=args.purpose)
        print_model(file)

    @staticmethod
    def get(args: FileIDArgs) -> None:
        file = get_client().files.retrieve(file_id=args.id)
        print_model(file)

    @staticmethod
    def delete(args: FileIDArgs) -> None:
        file = get_client().files.delete(file_id=args.id)
        print_model(file)

    @staticmethod
    def list() -> None:
        files = get_client().files.list()
        for file in files:
            print_model(file)
