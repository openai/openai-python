import os

# OpenAI Python bindings.
#
# Originally forked from the MIT-licensed Stripe Python bindings.

# Configuration variables

# Set this to the API key for whatever API provider you're using.
api_key = os.environ.get("OPENAI_API_KEY")
# Provide a function that takes the above key and returns a dictionary
# with the appropriate header(s) for whatever API provider you're using.
api_key_to_header_fn = lambda key: {"Authorization": f"Bearer {key}"}
organization = os.environ.get("OPENAI_ORGANIZATION")
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
