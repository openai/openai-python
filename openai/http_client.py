from __future__ import absolute_import, division, print_function

import sys
import textwrap
import warnings
import email
import time
import random
import threading
import json

import openai
from openai import error, util, six
from openai.request_metrics import RequestMetrics

# - Requests is the preferred HTTP library
# - Google App Engine has urlfetch
# - Use Pycurl if it's there (at least it verifies SSL certs)
# - Fall back to urllib2 with a warning if needed
try:
    from openai.six.moves import urllib
except ImportError:
    # Try to load in urllib2, but don't sweat it if it's not available.
    pass

try:
    import pycurl
except ImportError:
    pycurl = None

try:
    import requests
except ImportError:
    requests = None
else:
    try:
        # Require version 0.8.8, but don't want to depend on distutils
        version = requests.__version__
        major, minor, patch = [int(i) for i in version.split(".")]
    except Exception:
        # Probably some new-fangled version, so it should support verify
        pass
    else:
        if (major, minor, patch) < (0, 8, 8):
            sys.stderr.write(
                "Warning: the OpenAI library requires that your Python "
                '"requests" library be newer than version 0.8.8, but your '
                '"requests" library is version %s. OpenAI will fall back to '
                "an alternate HTTP library so everything should work. We "
                'recommend upgrading your "requests" library. If you have any '
                "questions, please contact support@openai.com. (HINT: running "
                '"pip install -U requests" should upgrade your requests '
                "library to the latest version.)" % (version,)
            )
            requests = None

try:
    from google.appengine.api import urlfetch
except ImportError:
    urlfetch = None

# proxy support for the pycurl client
from openai.six.moves.urllib.parse import urlparse


def _now_ms():
    return int(round(time.time() * 1000))


def new_default_http_client(*args, **kwargs):
    if urlfetch:
        impl = UrlFetchClient
    elif requests:
        impl = RequestsClient
    elif pycurl:
        impl = PycurlClient
    else:
        impl = Urllib2Client
        warnings.warn(
            "Warning: the OpenAI library is falling back to urllib2/urllib "
            "because neither requests nor pycurl are installed. "
            "urllib2's SSL implementation doesn't verify server "
            "certificates. For improved security, we suggest installing "
            "requests."
        )

    return impl(*args, **kwargs)


class HTTPClient(object):
    MAX_DELAY = 2
    INITIAL_DELAY = 0.5
    MAX_RETRY_AFTER = 60

    def __init__(self, verify_ssl_certs=True, proxy=None):
        self._verify_ssl_certs = verify_ssl_certs
        if proxy:
            if isinstance(proxy, str):
                proxy = {"http": proxy, "https": proxy}
            if not isinstance(proxy, dict):
                raise ValueError(
                    "Proxy(ies) must be specified as either a string "
                    "URL or a dict() with string URL under the"
                    " "
                    "https"
                    " and/or "
                    "http"
                    " keys."
                )
        self._proxy = proxy.copy() if proxy else None

        self._thread_local = threading.local()

    def request_with_retries(self, method, url, headers, post_data=None, stream=False):
        self._add_telemetry_header(headers)

        num_retries = 0

        while True:
            request_start = _now_ms()

            try:
                response = self.request(method, url, headers, post_data, stream=stream)
                connection_error = None
            except error.APIConnectionError as e:
                connection_error = e
                response = None

            if self._should_retry(response, connection_error, num_retries):
                if connection_error:
                    util.log_warn(
                        "Encountered a retryable error %s"
                        % connection_error.user_message
                    )
                num_retries += 1
                sleep_time = self._sleep_time_seconds(num_retries, response)
                util.log_info(
                    (
                        "Initiating retry %i for request %s %s after "
                        "sleeping %.2f seconds."
                        % (num_retries, method, url, sleep_time)
                    )
                )
                time.sleep(sleep_time)
            else:
                if response is not None:
                    self._record_request_metrics(response, request_start)

                    return response
                else:
                    raise connection_error

    def request(self, method, url, headers, post_data=None, stream=False):
        raise NotImplementedError("HTTPClient subclasses must implement `request`")

    def _should_retry(self, response, api_connection_error, num_retries):
        if num_retries >= self._max_network_retries():
            return False

        if response is None:
            # We generally want to retry on timeout and connection
            # exceptions, but defer this decision to underlying subclass
            # implementations. They should evaluate the driver-specific
            # errors worthy of retries, and set flag on the error returned.
            return api_connection_error.should_retry

        _, status_code, rheaders, _ = response

        # The API may ask us not to retry (eg; if doing so would be a no-op)
        # or advise us to retry (eg; in cases of lock timeouts); we defer to that.
        #
        # Note that we expect the headers object to be a CaseInsensitiveDict, as is the case with the requests library.
        if rheaders is not None and "openai-should-retry" in rheaders:
            if rheaders["openai-should-retry"] == "false":
                return False
            if rheaders["openai-should-retry"] == "true":
                return True

        # Retry on conflict errors.
        if status_code == 409:
            return True

        # Retry on 500, 503, and other internal errors.
        #
        # Note that we expect the openai-should-retry header to be false
        # in most cases when a 500 is returned, since our idempotency framework
        # would typically replay it anyway.
        if status_code >= 500:
            return True

        return False

    def _max_network_retries(self):
        from openai import max_network_retries

        # Configured retries, isolated here for tests
        return max_network_retries

    def _retry_after_header(self, response=None):
        if response is None:
            return None
        _, _, rheaders, _ = response

        try:
            return int(rheaders["retry-after"])
        except (KeyError, ValueError):
            return None

    def _sleep_time_seconds(self, num_retries, response=None):
        # Apply exponential backoff with initial_network_retry_delay on the
        # number of num_retries so far as inputs.
        # Do not allow the number to exceed max_network_retry_delay.
        sleep_seconds = min(
            HTTPClient.INITIAL_DELAY * (2 ** (num_retries - 1)), HTTPClient.MAX_DELAY
        )

        sleep_seconds = self._add_jitter_time(sleep_seconds)

        # But never sleep less than the base sleep seconds.
        sleep_seconds = max(HTTPClient.INITIAL_DELAY, sleep_seconds)

        # And never sleep less than the time the API asks us to wait, assuming it's a reasonable ask.
        retry_after = self._retry_after_header(response) or 0
        if retry_after <= HTTPClient.MAX_RETRY_AFTER:
            sleep_seconds = max(retry_after, sleep_seconds)

        return sleep_seconds

    def _add_jitter_time(self, sleep_seconds):
        # Randomize the value in [(sleep_seconds/ 2) to (sleep_seconds)]
        # Also separated method here to isolate randomness for tests
        sleep_seconds *= 0.5 * (1 + random.uniform(0, 1))
        return sleep_seconds

    def _add_telemetry_header(self, headers):
        last_request_metrics = getattr(self._thread_local, "last_request_metrics", None)
        if openai.enable_telemetry and last_request_metrics:
            telemetry = {"last_request_metrics": last_request_metrics.payload()}
            headers["X-OpenAI-Client-Telemetry"] = json.dumps(telemetry)

    def _record_request_metrics(self, response, request_start):
        _, _, rheaders, _ = response
        if "Request-Id" in rheaders and openai.enable_telemetry:
            request_id = rheaders["Request-Id"]
            request_duration_ms = _now_ms() - request_start
            self._thread_local.last_request_metrics = RequestMetrics(
                request_id, request_duration_ms
            )

    def close(self):
        raise NotImplementedError("HTTPClient subclasses must implement `close`")


class RequestsClient(HTTPClient):
    name = "requests"

    def __init__(self, timeout=600, session=None, **kwargs):
        super(RequestsClient, self).__init__(**kwargs)
        self._session = session
        self._timeout = timeout

    def request(self, method, url, headers, post_data=None, stream=False):
        kwargs = {}
        if self._verify_ssl_certs:
            kwargs["verify"] = openai.ca_bundle_path
        else:
            kwargs["verify"] = False

        if self._proxy:
            kwargs["proxies"] = self._proxy

        if getattr(self._thread_local, "session", None) is None:
            self._thread_local.session = self._session or requests.Session()

        try:
            try:
                result = self._thread_local.session.request(
                    method,
                    url,
                    headers=headers,
                    data=post_data,
                    timeout=self._timeout,
                    stream=stream,
                    **kwargs
                )
            except TypeError as e:
                raise TypeError(
                    "Warning: It looks like your installed version of the "
                    '"requests" library is not compatible with OpenAI\'s '
                    "usage thereof. (HINT: The most likely cause is that "
                    'your "requests" library is out of date. You can fix '
                    'that by running "pip install -U requests".) The '
                    "underlying error was: %s" % (e,)
                )

            # This causes the content to actually be read, which could cause
            # e.g. a socket timeout. TODO: The other fetch methods probably
            # are susceptible to the same and should be updated.
            if stream and "text/event-stream" in result.headers.get("Content-Type", ""):
                content = result.iter_lines()
                stream = True
            else:
                content = result.content
                stream = False
            status_code = result.status_code
        except Exception as e:
            # Would catch just requests.exceptions.RequestException, but can
            # also raise ValueError, RuntimeError, etc.
            self._handle_request_error(e)
        return content, status_code, result.headers, stream

    def _handle_request_error(self, e):
        # Catch SSL error first as it belongs to ConnectionError,
        # but we don't want to retry, unless it is caused by dropped
        # SSL connection
        if isinstance(e, requests.exceptions.SSLError):
            if 'ECONNRESET' not in repr(e):
                msg = (
                    "Could not verify OpenAI's SSL certificate.  Please make "
                    "sure that your network is not intercepting certificates.  "
                    "If this problem persists, let us know at "
                    "support@openai.com."
                )
                should_retry = False
            else:
                msg = "Detected ECONNRESET, indicates a dropped SSL connection."
                should_retry = True
            err = "%s: %s" % (type(e).__name__, str(e))
        # Retry only timeout and connect errors; similar to urllib3 Retry
        elif isinstance(
            e, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)
        ):
            msg = (
                "Unexpected error communicating with OpenAI.  "
                "If this problem persists, let us know at "
                "support@openai.com."
            )
            err = "%s: %s" % (type(e).__name__, str(e))
            should_retry = True
        # Catch remaining request exceptions
        elif isinstance(e, requests.exceptions.RequestException):
            msg = (
                "Unexpected error communicating with OpenAI.  "
                "If this problem persists, let us know at "
                "support@openai.com."
            )
            err = "%s: %s" % (type(e).__name__, str(e))
            should_retry = False
        else:
            msg = (
                "Unexpected error communicating with OpenAI. "
                "It looks like there's probably a configuration "
                "issue locally.  If this problem persists, let us "
                "know at support@openai.com."
            )
            err = "A %s was raised" % (type(e).__name__,)
            if str(e):
                err += " with error message %s" % (str(e),)
            else:
                err += " with no error message"
            should_retry = False

        if isinstance(e, requests.RequestException):
            request = e.request  # type: requests.Request
            if request is not None:
                err += " (url=" + self._sanitized_url(request.url) + ")"

        msg = textwrap.fill(msg) + "\n\n(Network error: %s)" % (err,)
        raise error.APIConnectionError(msg, should_retry=should_retry)

    @staticmethod
    def _sanitized_url(url):
        """ for now just strip all query params from the url for privacy"""
        url = urlparse(url)
        return url.scheme + "://" + url.netloc + url.path

    def close(self):
        if getattr(self._thread_local, "session", None) is not None:
            self._thread_local.session.close()


class UrlFetchClient(HTTPClient):
    name = "urlfetch"

    def __init__(self, verify_ssl_certs=True, proxy=None, deadline=55):
        super(UrlFetchClient, self).__init__(
            verify_ssl_certs=verify_ssl_certs, proxy=proxy
        )

        # no proxy support in urlfetch. for a patch, see:
        # https://code.google.com/p/googleappengine/issues/detail?id=544
        if proxy:
            raise ValueError(
                "No proxy support in urlfetch library. "
                "Set openai.default_http_client to either RequestsClient, "
                "PycurlClient, or Urllib2Client instance to use a proxy."
            )

        self._verify_ssl_certs = verify_ssl_certs
        # GAE requests time out after 60 seconds, so make sure to default
        # to 55 seconds to allow for a slow OpenAI
        self._deadline = deadline

    def request(self, method, url, headers, post_data=None, stream=False):
        if stream:
            raise NotImplementedError("Stream not yet implemented for {}".format(self))
        try:
            result = urlfetch.fetch(
                url=url,
                method=method,
                headers=headers,
                # Google App Engine doesn't let us specify our own cert bundle.
                # However, that's ok because the CA bundle they use recognizes
                # api.openai.com.
                validate_certificate=self._verify_ssl_certs,
                deadline=self._deadline,
                payload=post_data,
            )
        except urlfetch.Error as e:
            self._handle_request_error(e, url)

        return result.content, result.status_code, result.headers, stream

    def _handle_request_error(self, e, url):
        if isinstance(e, urlfetch.InvalidURLError):
            msg = (
                "The OpenAI library attempted to fetch an "
                "invalid URL (%r). This is likely due to a bug "
                "in the OpenAI Python bindings. Please let us know "
                "at support@openai.com." % (url,)
            )
        elif isinstance(e, urlfetch.DownloadError):
            msg = "There was a problem retrieving data from OpenAI."
        elif isinstance(e, urlfetch.ResponseTooLargeError):
            msg = (
                "There was a problem receiving all of your data from "
                "OpenAI.  This is likely due to a bug in OpenAI. "
                "Please let us know at support@openai.com."
            )
        else:
            msg = (
                "Unexpected error communicating with OpenAI. If this "
                "problem persists, let us know at support@openai.com."
            )

        msg = textwrap.fill(msg) + "\n\n(Network error: " + str(e) + ")"
        raise error.APIConnectionError(msg)

    def close(self):
        pass


class PycurlClient(HTTPClient):
    name = "pycurl"

    def __init__(self, verify_ssl_certs=True, proxy=None):
        super(PycurlClient, self).__init__(
            verify_ssl_certs=verify_ssl_certs, proxy=proxy
        )

        # Initialize this within the object so that we can reuse connections.
        self._curl = pycurl.Curl()

        # need to urlparse the proxy, since PyCurl
        # consumes the proxy url in small pieces
        if self._proxy:
            # now that we have the parser, get the proxy url pieces
            proxy = self._proxy
            for scheme, value in six.iteritems(proxy):
                proxy[scheme] = urlparse(value)

    def parse_headers(self, data):
        if "\r\n" not in data:
            return {}
        raw_headers = data.split("\r\n", 1)[1]
        headers = email.message_from_string(raw_headers)
        return dict((k.lower(), v) for k, v in six.iteritems(dict(headers)))

    def request(self, method, url, headers, post_data=None, stream=False):
        if stream:
            raise NotImplementedError("Stream not yet implemented for {}".format(self))
        b = util.io.BytesIO()
        rheaders = util.io.BytesIO()

        # Pycurl's design is a little weird: although we set per-request
        # options on this object, it's also capable of maintaining established
        # connections. Here we call reset() between uses to make sure it's in a
        # pristine state, but notably reset() doesn't reset connections, so we
        # still get to take advantage of those by virtue of re-using the same
        # object.
        self._curl.reset()

        proxy = self._get_proxy(url)
        if proxy:
            if proxy.hostname:
                self._curl.setopt(pycurl.PROXY, proxy.hostname)
            if proxy.port:
                self._curl.setopt(pycurl.PROXYPORT, proxy.port)
            if proxy.username or proxy.password:
                self._curl.setopt(
                    pycurl.PROXYUSERPWD, "%s:%s" % (proxy.username, proxy.password)
                )

        if method == "get":
            self._curl.setopt(pycurl.HTTPGET, 1)
        elif method == "post":
            self._curl.setopt(pycurl.POST, 1)
            self._curl.setopt(pycurl.POSTFIELDS, post_data)
        else:
            self._curl.setopt(pycurl.CUSTOMREQUEST, method.upper())

        # pycurl doesn't like unicode URLs
        self._curl.setopt(pycurl.URL, util.utf8(url))

        self._curl.setopt(pycurl.WRITEFUNCTION, b.write)
        self._curl.setopt(pycurl.HEADERFUNCTION, rheaders.write)
        self._curl.setopt(pycurl.NOSIGNAL, 1)
        self._curl.setopt(pycurl.CONNECTTIMEOUT, 30)
        self._curl.setopt(pycurl.TIMEOUT, 80)
        self._curl.setopt(
            pycurl.HTTPHEADER,
            ["%s: %s" % (k, v) for k, v in six.iteritems(dict(headers))],
        )
        if self._verify_ssl_certs:
            self._curl.setopt(pycurl.CAINFO, openai.ca_bundle_path)
        else:
            self._curl.setopt(pycurl.SSL_VERIFYHOST, False)

        try:
            self._curl.perform()
        except pycurl.error as e:
            self._handle_request_error(e)
        rbody = b.getvalue().decode("utf-8")
        rcode = self._curl.getinfo(pycurl.RESPONSE_CODE)
        headers = self.parse_headers(rheaders.getvalue().decode("utf-8"))

        return rbody, rcode, headers, stream

    def _handle_request_error(self, e):
        if e.args[0] in [
            pycurl.E_COULDNT_CONNECT,
            pycurl.E_COULDNT_RESOLVE_HOST,
            pycurl.E_OPERATION_TIMEOUTED,
        ]:
            msg = (
                "Could not connect to OpenAI.  Please check your "
                "internet connection and try again.  If this problem "
                "persists, you should check OpenAI's service status at "
                "https://twitter.com/openaistatus, or let us know at "
                "support@openai.com."
            )
            should_retry = True
        elif e.args[0] in [pycurl.E_SSL_CACERT, pycurl.E_SSL_PEER_CERTIFICATE]:
            msg = (
                "Could not verify OpenAI's SSL certificate.  Please make "
                "sure that your network is not intercepting certificates.  "
                "If this problem persists, let us know at "
                "support@openai.com."
            )
            should_retry = False
        else:
            msg = (
                "Unexpected error communicating with OpenAI. If this "
                "problem persists, let us know at support@openai.com."
            )
            should_retry = False

        msg = textwrap.fill(msg) + "\n\n(Network error: " + e.args[1] + ")"
        raise error.APIConnectionError(msg, should_retry=should_retry)

    def _get_proxy(self, url):
        if self._proxy:
            proxy = self._proxy
            scheme = url.split(":")[0] if url else None
            if scheme:
                return proxy.get(scheme, proxy.get(scheme[0:-1]))
        return None

    def close(self):
        pass


class Urllib2Client(HTTPClient):
    name = "urllib.request"

    def __init__(self, verify_ssl_certs=True, proxy=None):
        super(Urllib2Client, self).__init__(
            verify_ssl_certs=verify_ssl_certs, proxy=proxy
        )
        # prepare and cache proxy tied opener here
        self._opener = None
        if self._proxy:
            proxy = urllib.request.ProxyHandler(self._proxy)
            self._opener = urllib.request.build_opener(proxy)

    def request(self, method, url, headers, post_data=None, stream=False):
        if stream:
            raise NotImplementedError("Stream not yet implemented for {}".format(self))
        if six.PY3 and isinstance(post_data, six.string_types):
            post_data = post_data.encode("utf-8")

        req = urllib.request.Request(url, post_data, headers)

        if method not in ("get", "post"):
            req.get_method = lambda: method.upper()

        try:
            # use the custom proxy tied opener, if any.
            # otherwise, fall to the default urllib opener.
            response = (
                self._opener.open(req) if self._opener else urllib.request.urlopen(req)
            )
            rbody = response.read()
            rcode = response.code
            headers = dict(response.info())
        except urllib.error.HTTPError as e:
            rcode = e.code
            rbody = e.read()
            headers = dict(e.info())
        except (urllib.error.URLError, ValueError) as e:
            self._handle_request_error(e)
        lh = dict((k.lower(), v) for k, v in six.iteritems(dict(headers)))
        return rbody, rcode, lh, stream

    def _handle_request_error(self, e):
        msg = (
            "Unexpected error communicating with OpenAI. "
            "If this problem persists, let us know at support@openai.com."
        )
        msg = textwrap.fill(msg) + "\n\n(Network error: " + str(e) + ")"
        raise error.APIConnectionError(msg)

    def close(self):
        pass
