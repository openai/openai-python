import calendar
import datetime
import json
import platform
import time
import uuid
import warnings
from io import BytesIO
from collections import OrderedDict
from urllib.parse import urlencode, urlsplit, urlunsplit

import openai
from openai import error, http_client, version, util
from openai.multipart_data_generator import MultipartDataGenerator
from openai.openai_response import OpenAIResponse
from openai.upload_progress import BufferReader


def _encode_datetime(dttime) -> int:
    utc_timestamp: float
    if dttime.tzinfo and dttime.tzinfo.utcoffset(dttime) is not None:
        utc_timestamp = calendar.timegm(dttime.utctimetuple())
    else:
        utc_timestamp = time.mktime(dttime.timetuple())

    return int(utc_timestamp)


def _encode_nested_dict(key, data, fmt="%s[%s]"):
    d = OrderedDict()
    for subkey, subvalue in data.items():
        d[fmt % (key, subkey)] = subvalue
    return d


def _api_encode(data):
    for key, value in data.items():
        if value is None:
            continue
        elif hasattr(value, "openai_id"):
            yield (key, value.openai_id)
        elif isinstance(value, list) or isinstance(value, tuple):
            for i, sv in enumerate(value):
                if isinstance(sv, dict):
                    subdict = _encode_nested_dict("%s[%d]" % (key, i), sv)
                    for k, v in _api_encode(subdict):
                        yield (k, v)
                else:
                    yield ("%s[%d]" % (key, i), sv)
        elif isinstance(value, dict):
            subdict = _encode_nested_dict(key, value)
            for subkey, subvalue in _api_encode(subdict):
                yield (subkey, subvalue)
        elif isinstance(value, datetime.datetime):
            yield (key, _encode_datetime(value))
        else:
            yield (key, value)


def _build_api_url(url, query):
    scheme, netloc, path, base_query, fragment = urlsplit(url)

    if base_query:
        query = "%s&%s" % (base_query, query)

    return urlunsplit((scheme, netloc, path, query, fragment))


def parse_stream(rbody):
    for line in rbody:
        if line:
            if line == b"data: [DONE]":
                return
            if hasattr(line, "decode"):
                line = line.decode("utf-8")
            if line.startswith("data: "):
                line = line[len("data: ") :]
            yield line


class APIRequestor:
    def __init__(
        self, key=None, client=None, api_base=None, api_version=None, organization=None
    ):
        self.api_base = api_base or openai.api_base
        self.api_key = key
        self.api_version = api_version or openai.api_version
        self.organization = organization or openai.organization

        self._default_proxy = None

        from openai import verify_ssl_certs as verify
        from openai import proxy

        if client:
            self._client = client
        elif openai.default_http_client:
            self._client = openai.default_http_client
            if proxy != self._default_proxy:
                warnings.warn(
                    "openai.proxy was updated after sending a "
                    "request - this is a no-op. To use a different proxy, "
                    "set openai.default_http_client to a new client "
                    "configured with the proxy."
                )
        else:
            # If the openai.default_http_client has not been set by the user
            # yet, we'll set it here. This way, we aren't creating a new
            # HttpClient for every request.
            openai.default_http_client = http_client.new_default_http_client(
                verify_ssl_certs=verify, proxy=proxy
            )
            self._client = openai.default_http_client
            self._default_proxy = proxy

    @classmethod
    def format_app_info(cls, info):
        str = info["name"]
        if info["version"]:
            str += "/%s" % (info["version"],)
        if info["url"]:
            str += " (%s)" % (info["url"],)
        return str

    def request(self, method, url, params=None, headers=None, stream=False):
        rbody, rcode, rheaders, stream, my_api_key = self.request_raw(
            method.lower(), url, params, headers, stream=stream
        )
        resp = self.interpret_response(rbody, rcode, rheaders, stream=stream)
        return resp, stream, my_api_key

    def handle_error_response(self, rbody, rcode, resp, rheaders, stream_error=False):
        try:
            error_data = resp["error"]
        except (KeyError, TypeError):
            raise error.APIError(
                "Invalid response object from API: %r (HTTP response code "
                "was %d)" % (rbody, rcode),
                rbody,
                rcode,
                resp,
            )

        if "internal_message" in error_data:
            error_data["message"] += "\n\n" + error_data["internal_message"]

        util.log_info(
            "OpenAI API error received",
            error_code=error_data.get("code"),
            error_type=error_data.get("type"),
            error_message=error_data.get("message"),
            error_param=error_data.get("param"),
            stream_error=stream_error,
        )

        # Rate limits were previously coded as 400's with code 'rate_limit'
        if rcode == 429:
            return error.RateLimitError(
                error_data.get("message"), rbody, rcode, resp, rheaders
            )
        elif rcode in [400, 404, 415]:
            if error_data.get("type") == "idempotency_error":
                return error.IdempotencyError(
                    error_data.get("message"), rbody, rcode, resp, rheaders
                )
            else:
                return error.InvalidRequestError(
                    error_data.get("message"),
                    error_data.get("param"),
                    error_data.get("code"),
                    rbody,
                    rcode,
                    resp,
                    rheaders,
                )
        elif rcode == 401:
            return error.AuthenticationError(
                error_data.get("message"), rbody, rcode, resp, rheaders
            )
        elif rcode == 403:
            return error.PermissionError(
                error_data.get("message"), rbody, rcode, resp, rheaders
            )
        elif rcode == 409:
            return error.TryAgain(
                error_data.get("message"), rbody, rcode, resp, rheaders
            )
        elif stream_error:
            # TODO: we will soon attach status codes to stream errors
            parts = [error_data.get("message"), "(Error occurred while streaming.)"]
            message = " ".join([p for p in parts if p is not None])
            return error.APIError(message, rbody, rcode, resp, rheaders)
        else:
            return error.APIError(
                error_data.get("message"), rbody, rcode, resp, rheaders
            )

    def request_headers(self, api_key, method, extra):
        user_agent = "OpenAI/v1 PythonBindings/%s" % (version.VERSION,)
        if openai.app_info:
            user_agent += " " + self.format_app_info(openai.app_info)

        ua = {
            "bindings_version": version.VERSION,
            "httplib": self._client.name,
            "lang": "python",
            "lang_version": platform.python_version(),
            "platform": platform.platform(),
            "publisher": "openai",
            "uname": " ".join(platform.uname()),
        }
        if openai.app_info:
            ua["application"] = openai.app_info

        headers = {
            "X-OpenAI-Client-User-Agent": json.dumps(ua),
            "User-Agent": user_agent,
            "Authorization": "Bearer %s" % (api_key,),
        }

        if self.organization:
            headers["OpenAI-Organization"] = self.organization

        if method in {"post", "put"}:
            headers.setdefault("Idempotency-Key", str(uuid.uuid4()))

        if self.api_version is not None:
            headers["OpenAI-Version"] = self.api_version

        headers.update(extra)

        return headers

    def request_raw(
        self, method, url, params=None, supplied_headers=None, stream=False
    ):
        """
        Mechanism for issuing an API call
        """

        if self.api_key:
            my_api_key = self.api_key
        else:
            from openai import api_key

            my_api_key = api_key

        if my_api_key is None:
            raise error.AuthenticationError(
                "No API key provided. (HINT: set your API key in code using "
                '"openai.api_key = <API-KEY>", or you can set the environment variable OPENAI_API_KEY=<API-KEY>). You can generate API keys '
                "in the OpenAI web interface. See https://onboard.openai.com "
                "for details, or email support@openai.com if you have any "
                "questions."
            )

        abs_url = "%s%s" % (self.api_base, url)
        headers = {}
        compress = None
        progress_meter = False

        if method == "get" or method == "delete":
            if params:
                encoded_params = url_encode_params(params)
                abs_url = _build_api_url(abs_url, encoded_params)
            else:
                encoded_params = None
            post_data = None
        elif method in {"post", "put"}:
            if (
                supplied_headers is not None
                and supplied_headers.get("Content-Type") == "multipart/form-data"
            ):
                generator = MultipartDataGenerator()
                generator.add_params(params or {})
                post_data = generator.get_post_data()
                content_type = "multipart/form-data; boundary=%s" % (
                    generator.boundary,
                )
                # We will overrite Content-Type
                supplied_headers.pop("Content-Type")
                progress_meter = True
                # compress = "gzip"
                compress = None
            else:
                post_data = json.dumps(params).encode()
                content_type = "application/json"

            headers["Content-Type"] = content_type

            encoded_params = post_data

            if progress_meter:
                post_data = BufferReader(post_data, desc="Upload progress")

            if compress == "gzip":
                if not hasattr(post_data, "read"):
                    post_data = BytesIO(post_data)
                headers["Content-Encoding"] = "gzip"

                from openai.gzip_stream import GZIPCompressedStream

                post_data = GZIPCompressedStream(post_data, compression_level=9)
        else:
            raise error.APIConnectionError(
                "Unrecognized HTTP method %r. This may indicate a bug in the "
                "OpenAI bindings. Please contact support@openai.com for "
                "assistance." % (method,)
            )

        headers = self.request_headers(my_api_key, method, headers)
        if supplied_headers is not None:
            for key, value in supplied_headers.items():
                headers[key] = value

        util.log_info("Request to OpenAI API", method=method, path=abs_url)
        util.log_debug(
            "Post details", post_data=encoded_params, api_version=self.api_version
        )

        rbody, rcode, rheaders, stream = self._client.request_with_retries(
            method, abs_url, headers, post_data, stream=stream
        )

        util.log_info(
            "OpenAI API response",
            path=abs_url,
            response_code=rcode,
            processing_ms=rheaders.get("OpenAI-Processing-Ms"),
        )
        util.log_debug("API response body", body=rbody, headers=rheaders)

        if "Request-Id" in rheaders:
            request_id = rheaders["Request-Id"]
            util.log_debug(
                "Dashboard link for request", link=util.dashboard_link(request_id)
            )

        return rbody, rcode, rheaders, stream, my_api_key

    def interpret_response(self, rbody, rcode, rheaders, stream=False):
        if stream:
            return (
                self.interpret_response_line(line, rcode, rheaders, stream)
                for line in parse_stream(rbody)
            )
        else:
            return self.interpret_response_line(rbody, rcode, rheaders, stream)

    def interpret_response_line(self, rbody, rcode, rheaders, stream=False):
        try:
            if hasattr(rbody, "decode"):
                rbody = rbody.decode("utf-8")
            resp = OpenAIResponse(rbody, rcode, rheaders)
        except Exception:
            raise error.APIError(
                "Invalid response body from API: %s "
                "(HTTP response code was %d)" % (rbody, rcode),
                rbody,
                rcode,
                rheaders,
            )
        # In the future, we might add a "status" parameter to errors
        # to better handle the "error while streaming" case.
        stream_error = stream and "error" in resp.data
        if stream_error or not 200 <= rcode < 300:
            raise self.handle_error_response(
                rbody, rcode, resp.data, rheaders, stream_error=stream_error
            )

        return resp


def url_encode_params(params):
    encoded_params = urlencode(list(_api_encode(params or {})))

    # Don't use strict form encoding by changing the square bracket control
    # characters back to their literals. This is fine by the server, and
    # makes these parameter strings easier to read.
    encoded_params = encoded_params.replace("%5B", "[").replace("%5D", "]")
    return encoded_params
