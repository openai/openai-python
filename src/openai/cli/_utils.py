from __future__ import annotations

import sys

from .. import OpenAI
from .._compat import model_json
from .._models import BaseModel


class Colours:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


_client: OpenAI | None = None


def set_client(client: OpenAI) -> None:
    global _client

    _client = client


def get_client() -> OpenAI:
    if _client is None:
        raise RuntimeError("client instance has not been set yet")
    return _client


def organization_info() -> str:
    if _client is None:
        return ""

    organization = get_client().organization
    if organization is not None:
        return "[organization={}] ".format(organization)

    return ""


def print_model(model: BaseModel) -> None:
    sys.stdout.write(model_json(model, indent=2) + "\n")
