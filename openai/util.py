import functools
import hmac
import io
import logging
import os
import re
import sys
from urllib.parse import parse_qsl

import openai


OPENAI_LOG = os.environ.get("OPENAI_LOG")

logger = logging.getLogger("openai")

__all__ = [
    "io",
    "parse_qsl",
    "log_info",
    "log_debug",
    "log_warn",
    "dashboard_link",
    "logfmt",
]


def is_appengine_dev():
    return "APPENGINE_RUNTIME" in os.environ and "Dev" in os.environ.get(
        "SERVER_SOFTWARE", ""
    )


def _console_log_level():
    if openai.log in ["debug", "info"]:
        return openai.log
    elif OPENAI_LOG in ["debug", "info"]:
        return OPENAI_LOG
    else:
        return None


def log_debug(message, **params):
    msg = logfmt(dict(message=message, **params))
    if _console_log_level() == "debug":
        print(msg, file=sys.stderr)
    logger.debug(msg)


def log_info(message, **params):
    msg = logfmt(dict(message=message, **params))
    if _console_log_level() in ["debug", "info"]:
        print(msg, file=sys.stderr)
    logger.info(msg)


def log_warn(message, **params):
    msg = logfmt(dict(message=message, **params))
    print(msg, file=sys.stderr)
    logger.warn(msg)


def _test_or_live_environment():
    if openai.api_key is None:
        return
    match = re.match(r"sk_(live|test)_", openai.api_key)
    if match is None:
        return
    return match.groups()[0]


def dashboard_link(request_id):
    return "https://dashboard.openai.com/{env}/logs/{reqid}".format(
        env=_test_or_live_environment() or "test", reqid=request_id
    )


def logfmt(props):
    def fmt(key, val):
        # Handle case where val is a bytes or bytesarray
        if hasattr(val, "decode"):
            val = val.decode("utf-8")
        # Check if val is already a string to avoid re-encoding into ascii.
        if not isinstance(val, str):
            val = str(val)
        if re.search(r"\s", val):
            val = repr(val)
        # key should already be a string
        if re.search(r"\s", key):
            key = repr(key)
        return "{key}={val}".format(key=key, val=val)

    return " ".join([fmt(key, val) for key, val in sorted(props.items())])


def secure_compare(val1, val2):
    return hmac.compare_digest(val1, val2)


def get_object_classes():
    # This is here to avoid a circular dependency
    from openai.object_classes import OBJECT_CLASSES

    return OBJECT_CLASSES


def convert_to_openai_object(
    resp,
    api_key=None,
    api_version=None,
    organization=None,
    engine=None,
    plain_old_data=False,
):
    # If we get a OpenAIResponse, we'll want to return a
    # OpenAIObject with the last_response field filled out with
    # the raw API response information
    openai_response = None

    if isinstance(resp, openai.openai_response.OpenAIResponse):
        # TODO: move this elsewhere
        openai_response = resp
        resp = openai_response.data
        organization = (
            openai_response.headers.get("OpenAI-Organization") or organization
        )

    if plain_old_data:
        return resp
    elif isinstance(resp, list):
        return [
            convert_to_openai_object(
                i, api_key, api_version, organization, engine=engine
            )
            for i in resp
        ]
    elif isinstance(resp, dict) and not isinstance(
        resp, openai.openai_object.OpenAIObject
    ):
        resp = resp.copy()
        klass_name = resp.get("object")
        if isinstance(klass_name, str):
            klass = get_object_classes().get(
                klass_name, openai.openai_object.OpenAIObject
            )
        else:
            klass = openai.openai_object.OpenAIObject

        return klass.construct_from(
            resp,
            api_key,
            api_version=api_version,
            organization=organization,
            last_response=openai_response,
            engine=engine,
        )
    else:
        return resp


def convert_to_dict(obj):
    """Converts a OpenAIObject back to a regular dict.

    Nested OpenAIObjects are also converted back to regular dicts.

    :param obj: The OpenAIObject to convert.

    :returns: The OpenAIObject as a dict.
    """
    if isinstance(obj, list):
        return [convert_to_dict(i) for i in obj]
    # This works by virtue of the fact that OpenAIObjects _are_ dicts. The dict
    # comprehension returns a regular dict and recursively applies the
    # conversion to each value.
    elif isinstance(obj, dict):
        return {k: convert_to_dict(v) for k, v in obj.items()}
    else:
        return obj


def populate_headers(idempotency_key=None, request_id=None):
    headers = {}
    if idempotency_key is not None:
        headers["Idempotency-Key"] = idempotency_key
    if request_id is not None:
        headers["X-Request-Id"] = request_id
    if openai.debug:
        headers["OpenAI-Debug"] = "true"

    return headers


def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


class class_method_variant(object):
    def __init__(self, class_method_name):
        self.class_method_name = class_method_name

    def __call__(self, method):
        self.method = method
        return self

    def __get__(self, obj, objtype=None):
        @functools.wraps(self.method)
        def _wrapper(*args, **kwargs):
            if obj is not None:
                # Method was called as an instance method, e.g.
                # instance.method(...)
                return self.method(obj, *args, **kwargs)
            elif len(args) > 0 and isinstance(args[0], objtype):
                # Method was called as a class method with the instance as the
                # first argument, e.g. Class.method(instance, ...) which in
                # Python is the same thing as calling an instance method
                return self.method(args[0], *args[1:], **kwargs)
            else:
                # Method was called as a class method, e.g. Class.method(...)
                class_method = getattr(objtype, self.class_method_name)
                return class_method(*args, **kwargs)

        return _wrapper
