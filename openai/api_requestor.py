from email import header
import json
import platform
import threading
import warnings
from json import JSONDecodeError
from typing import Dict, Iterator, Optional, Tuple, Union
from urllib.parse import urlencode, urlsplit, urlunsplit

import requests

import openai
from openai import error, util, version
from openai.openai_response import OpenAIResponse
from openai.util import ApiType

TIMEOUT_SECS = 600
MAX_CONNECTION_RETRIES = 2

# Has one attribute per thread, 'session'.
_thread_context = threading.local()


def _build_api_url(url, query):
    scheme, netloc, path, base_query, fragment = urlsplit(url)

    if base_query:
        query = "%s&%s" % (base_query, query)

    return urlunsplit((scheme, netloc, path, query, fragment))


def _requests_proxies_arg(proxy) -> Optional[Dict[str, str]]:
    """Returns a value suitable for the 'proxies' argument to 'requests.request."""
    if proxy is None:
        return None
    elif isinstance(proxy, str):
        return {"http": proxy, "https": proxy}
    elif isinstance(proxy, dict):
        return proxy.copy()
    else:
        raise ValueError(
            "'openai.proxy' must be specified as either a string URL or a dict with string URL under the https and/or http keys."
        )


def _make_session() -> requests.Session:
    if not openai.verify_ssl_certs:
        warnings.warn("verify_ssl_certs is ignored; openai always verifies.")
    s = requests.Session()
    proxies = _requests_proxies_arg(openai.proxy)
    if proxies:
        s.proxies = proxies
    s.mount(
        "https://",
        requests.adapters.HTTPAdapter(max_retries=MAX_CONNECTION_RETRIES),
    )
    return s


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
    def __init__(self, key=None, api_base=None, api_type=None, api_version=None, organization=None):
        self.api_base = api_base or openai.api_base
        self.api_key = key or util.default_api_key()
        self.api_type = ApiType.from_str(api_type) if api_type else ApiType.from_str(openai.api_type)
        self.api_version = api_version or openai.api_version
        self.organization = organization or openai.organization

    @classmethod
    def format_app_info(cls, info):
        str = info["name"]
        if info["version"]:
            str += "/%s" % (info["version"],)
        if info["url"]:
            str += " (%s)" % (info["url"],)
        return str

    def request(
        self,
        method,
        url,
        params=None,
        headers=None,
        files=None,
        stream=False,
        request_id: Optional[str] = None,
    ) -> Tuple[Union[OpenAIResponse, Iterator[OpenAIResponse]], bool, str]:
        result = self.request_raw(
            method.lower(),
            url,
            params,
            headers,
            files=files,
            stream=stream,
            request_id=request_id,
        )
        resp, got_stream = self._interpret_response(result, stream)
        return resp, got_stream, self.api_key

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

    def request_headers(
        self, method: str, extra, request_id: Optional[str]
    ) -> Dict[str, str]:
        user_agent = "OpenAI/v1 PythonBindings/%s" % (version.VERSION,)
        if openai.app_info:
            user_agent += " " + self.format_app_info(openai.app_info)

        uname_without_node = " ".join(
            v for k, v in platform.uname()._asdict().items() if k != "node"
        )
        ua = {
            "bindings_version": version.VERSION,
            "httplib": "requests",
            "lang": "python",
            "lang_version": platform.python_version(),
            "platform": platform.platform(),
            "publisher": "openai",
            "uname": uname_without_node,
        }
        if openai.app_info:
            ua["application"] = openai.app_info

        headers = {
            "X-OpenAI-Client-User-Agent": json.dumps(ua),
            "User-Agent": user_agent,
        }

        headers.update(util.api_key_to_header(self.api_type, self.api_key))

        if self.organization:
            headers["OpenAI-Organization"] = self.organization

        if self.api_version is not None and self.api_type == ApiType.OPEN_AI:
            headers["OpenAI-Version"] = self.api_version
        if request_id is not None:
            headers["X-Request-Id"] = request_id
        if openai.debug:
            headers["OpenAI-Debug"] = "true"
        headers.update(extra)

        return headers

    def request_raw(
        self,
        method,
        url,
        params=None,
        supplied_headers=None,
        files=None,
        stream=False,
        request_id: Optional[str] = None,
    ) -> requests.Response:
        abs_url = "%s%s" % (self.api_base, url)
        headers = {}

        data = None
        if method == "get" or method == "delete":
            if params:
                encoded_params = urlencode(
                    [(k, v) for k, v in params.items() if v is not None]
                )
                abs_url = _build_api_url(abs_url, encoded_params)
        elif method in {"post", "put"}:
            if params and files:
                raise ValueError("At most one of params and files may be specified.")
            if params:
                data = json.dumps(params).encode()
                headers["Content-Type"] = "application/json"
        else:
            raise error.APIConnectionError(
                "Unrecognized HTTP method %r. This may indicate a bug in the "
                "OpenAI bindings. Please contact support@openai.com for "
                "assistance." % (method,)
            )

        headers = self.request_headers(method, headers, request_id)
        if supplied_headers is not None:
            headers.update(supplied_headers)

        util.log_info("Request to OpenAI API", method=method, path=abs_url)
        util.log_debug("Post details", data=data, api_version=self.api_version)

        if not hasattr(_thread_context, "session"):
            _thread_context.session = _make_session()
        try:
            result = _thread_context.session.request(
                method,
                abs_url,
                headers=headers,
                data=data,
                files=files,
                stream=stream,
                timeout=TIMEOUT_SECS,
            )
        except requests.exceptions.RequestException as e:
            raise error.APIConnectionError("Error communicating with OpenAI") from e
        util.log_info(
            "OpenAI API response",
            path=abs_url,
            response_code=result.status_code,
            processing_ms=result.headers.get("OpenAI-Processing-Ms"),
        )
        # Don't read the whole stream for debug logging unless necessary.
        if openai.log == "debug":
            util.log_debug(
                "API response body", body=result.content, headers=result.headers
            )
        return result

    def _interpret_response(
        self, result: requests.Response, stream: bool
    ) -> Tuple[Union[OpenAIResponse, Iterator[OpenAIResponse]], bool]:
        """Returns the response(s) and a bool indicating whether it is a stream."""
        if stream and "text/event-stream" in result.headers.get("Content-Type", ""):
            return (
                self._interpret_response_line(
                    line, result.status_code, result.headers, stream=True
                )
                for line in parse_stream(result.iter_lines())
            ), True
        else:
            return (
                self._interpret_response_line(
                    result.content, result.status_code, result.headers, stream=False
                ),
                False,
            )

    def _interpret_response_line(
        self, rbody, rcode, rheaders, stream: bool
    ) -> OpenAIResponse:
        if rcode == 503:
            raise error.ServiceUnavailableError(
                "The server is overloaded or not ready yet.", rbody, rcode, headers=rheaders
            )
        try:
            if hasattr(rbody, "decode"):
                rbody = rbody.decode("utf-8")
            data = json.loads(rbody)
        except (JSONDecodeError, UnicodeDecodeError):
            raise error.APIError(
                f"HTTP code {rcode} from API ({rbody})", rbody, rcode, headers=rheaders
            )
        resp = OpenAIResponse(data, rheaders)
        # In the future, we might add a "status" parameter to errors
        # to better handle the "error while streaming" case.
        stream_error = stream and "error" in resp.data
        if stream_error or not 200 <= rcode < 300:
            raise self.handle_error_response(
                rbody, rcode, resp.data, rheaders, stream_error=stream_error
            )
        return resp
