import os
import configparser

# OpenAI Python bindings.
#
# Originally forked from the MIT-licensed Stripe Python bindings.

# Configuration variables

api_key = os.environ.get("OPENAI_API_KEY")
organization = os.environ.get("OPENAI_ORGANIZATION")

home = os.path.expanduser("~")
config_home = os.environ.get("XDG_CONFIG_HOME", os.path.join(home, ".config"))
config_parser = configparser.RawConfigParser()
config_location = os.path.join(config_home, "openairc")
if os.path.exists(config_location):
    config_parser.read(config_location)

    if not api_key:
        api_key = config_parser.get("api", "APIKey")

    if not organization:
        organization = config_parser.get("api", "Organization")


client_id = None
api_base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com")
file_api_base = None
api_version = None
verify_ssl_certs = True
proxy = None
default_http_client = None
app_info = None
enable_telemetry = True
max_network_retries = 0
ca_bundle_path = os.path.join(os.path.dirname(__file__), "data/ca-certificates.crt")
debug = False

# Set to either 'debug' or 'info', controls console logging
log = None

# API resources
from openai.api_resources import (  # noqa: E402,F401
    Answer,
    Classification,
    Completion,
    Engine,
    ErrorObject,
    File,
    FineTune,
    Model,
    Search,
)
from openai.error import APIError, InvalidRequestError, OpenAIError  # noqa: E402,F401
