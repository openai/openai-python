# OpenAI Python bindings.
#
# Originally forked from the MIT-licensed Stripe Python bindings.

import os
from typing import Optional

from openai.api_resources import (
    Answer,
    Classification,
    Completion,
    Customer,
    Edit,
    Deployment,
    Embedding,
    Engine,
    ErrorObject,
    File,
    FineTune,
    Image,
    Model,
    Moderation,
    Search,
)
from openai.error import APIError, InvalidRequestError, OpenAIError

api_key = os.environ.get("OPENAI_API_KEY")
# Path of a file with an API key, whose contents can change. Supercedes
# `api_key` if set.  The main use case is volume-mounted Kubernetes secrets,
# which are updated automatically.
api_key_path: Optional[str] = os.environ.get("OPENAI_API_KEY_PATH")

organization = os.environ.get("OPENAI_ORGANIZATION")
api_base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
api_type = os.environ.get("OPENAI_API_TYPE", "open_ai")
api_version = (
    "2022-03-01-preview" if api_type in ("azure", "azure_ad", "azuread") else None
)
verify_ssl_certs = True  # No effect. Certificates are always verified.
proxy = None
app_info = None
enable_telemetry = False  # Ignored; the telemetry feature was removed.
ca_bundle_path = None  # No longer used, feature was removed
debug = False
log = None  # Set to either 'debug' or 'info', controls console logging

__all__ = [
    "APIError",
    "Answer",
    "Classification",
    "Completion",
    "Customer",
    "Edit",
    "Image",
    "Deployment",
    "Embedding",
    "Engine",
    "ErrorObject",
    "File",
    "FineTune",
    "InvalidRequestError",
    "Model",
    "Moderation",
    "OpenAIError",
    "Search",
    "api_base",
    "api_key",
    "api_type",
    "api_key_path",
    "api_version",
    "app_info",
    "ca_bundle_path",
    "debug",
    "enable_elemetry",
    "log",
    "organization",
    "proxy",
    "verify_ssl_certs",
]
