from __future__ import annotations

import anyio
import httpx2


def _accepts_byte_ranges(response: httpx2.Response) -> bool:
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept-Ranges
    # the header is a comma-separated list of supported range units
    value = str(response.headers.get("accept-ranges", ""))
    return any(unit.strip() == "bytes" for unit in value.lower().split(","))


def _is_identity_encoded(response: httpx2.Response) -> bool:
    # byte ranges address the encoded representation, but `iter_bytes()` yields
    # decoded bytes — resuming is only sound when the two are the same
    value = str(response.headers.get("content-encoding", "")).strip().lower()
    return value in ("", "identity")


def _content_range_bounds(response: httpx2.Response) -> tuple[int, int | None, int | None] | None:
    """Parse a `206` response's `Content-Range: bytes <start>-<end>/<total>` header.

    `end` and `total` are `None` when absent or unknown (`*`). Range unit names
    are case-insensitive, so the header is normalised before parsing.
    """
    value = str(response.headers.get("content-range", "")).strip().lower()
    if not value.startswith("bytes "):
        return None
    try:
        start_part, rest = value[len("bytes ") :].split("-", 1)
        end_part, _, total_part = rest.partition("/")
        start = int(start_part.strip())
        end = int(end_part.strip()) if end_part.strip() not in ("", "*") else None
        total = int(total_part.strip()) if total_part.strip() not in ("", "*") else None
    except ValueError:
        return None
    return start, end, total


def _range_total_bytes(response: httpx2.Response) -> int | None:
    """Total size reported by a `416` response's `Content-Range: bytes */<total>` header."""
    value = str(response.headers.get("content-range", "")).strip().lower()
    prefix = "bytes */"
    if not value.startswith(prefix):
        return None
    try:
        return int(value[len(prefix) :].strip())
    except ValueError:
        return None


class _PartialDownload:
    """Bytes already received from a range-capable response body, plus the
    response (headers, request, validator) that produced them."""

    __slots__ = ("data", "representation")

    def __init__(self) -> None:
        self.data = bytearray()
        self.representation: httpx2.Response | None = None

    def __bool__(self) -> bool:
        return bool(self.data)

    def reset(self, response: httpx2.Response) -> None:
        self.data.clear()
        self.representation = response

    def clear(self) -> None:
        self.data.clear()
        self.representation = None


def _resume_validator(response: httpx2.Response) -> str | None:
    """Strong validator for an `If-Range` request, from the interrupted response.

    Only a strong `ETag` qualifies: a weak `W/` tag is explicitly unusable, and
    a `Last-Modified` date cannot be assumed to be a strong validator (its
    one-second granularity may hide changes), so both fall back to "no
    validator" and the download restarts instead of being resumed.
    """
    etag = str(response.headers.get("etag", "")).strip()
    if etag and not etag.startswith("W/"):
        return etag
    return None


def _reassembled_download_response(
    representation: httpx2.Response,
    content: bytes,
    *,
    elapsed_from: httpx2.Response,
) -> httpx2.Response:
    headers = [
        (key, value)
        for key, value in representation.headers.raw
        if key.decode("latin-1").lower() not in ("content-range", "content-length", "transfer-encoding", "x-request-id")
    ]
    # the request id belongs to the exchange that completed the transfer, so
    # it must agree with the request/extensions/elapsed taken from that
    # attempt below rather than with the interrupted one
    headers.extend(
        (key, value) for key, value in elapsed_from.headers.raw if key.decode("latin-1").lower() == "x-request-id"
    )
    # keep the response class of the client that actually served the request
    # (legacy `httpx` clients produce legacy `httpx.Response` objects)
    response_cls = httpx2.Response if isinstance(representation, httpx2.Response) else type(representation)
    rebuilt = response_cls(
        200,
        headers=headers,
        content=content,
        # the request/response metadata of the attempt that completed the
        # transfer (its final URL after redirects, its request id extensions)
        request=elapsed_from.request,
        extensions=elapsed_from.extensions,
        history=elapsed_from.history,
    )
    # keep the encoding state the serving client attached: the client-level
    # `default_encoding` is copied as-is (a plain name, or a detector callable
    # which then runs against the assembled body), while an encoding that was
    # explicitly pinned on the interrupted response is preserved verbatim —
    # a merely header-derived encoding is left to re-derive from the copied
    # `Content-Type` header so a callable detector sees the full body
    rebuilt.default_encoding = representation.default_encoding
    explicit_encoding = getattr(representation, "_encoding", None)
    if explicit_encoding is not None:
        rebuilt.encoding = explicit_encoding
    try:
        rebuilt.elapsed = elapsed_from.elapsed
    except RuntimeError:
        # the serving transport did not record timing; leave the field unset
        # exactly as an unread response would be
        pass
    return rebuilt


def _read_and_release(response: httpx2.Response) -> None:
    """Read a streamed response to completion, closing it if the read fails."""
    try:
        response.read()
    except BaseException:
        response.close()
        raise


async def _aread_and_release(response: httpx2.Response) -> None:
    """Async counterpart of `_read_and_release`."""
    try:
        await response.aread()
    except BaseException:
        with anyio.CancelScope(shield=True):
            await response.aclose()
        raise


def read_resumable_body(
    response: httpx2.Response,
    partial: _PartialDownload,
) -> httpx2.Response:
    """Read a non-streamed GET response body, resuming interrupted downloads.

    Retries normally restart a failed download from the first byte, which can
    never succeed when a transfer is deterministically cut off mid-body (for
    example large Batch API result files). When the server advertises
    `Accept-Ranges: bytes`, later attempts request only the bytes that are
    still missing, so retries make forward progress instead of repeating it.
    """
    resuming = bool(partial)
    if resuming and response.status_code == 416:
        total = _range_total_bytes(response)
        representation = partial.representation
        assert representation is not None
        if total is not None and total == len(partial.data):
            # the earlier attempt already received every byte; only the
            # terminating chunks went missing; read the (small) body so a
            # retained reference sees a normally-consumed response
            _read_and_release(response)
            return finish_download(partial, elapsed_from=response)
        received = len(partial.data)
        response.close()
        partial.clear()
        raise httpx2.ReadError(
            f"Server rejected resuming the download at byte {received} with 416; restarting from scratch",
            request=representation.request,
        )

    accumulate = False
    if resuming and response.status_code == 206:
        bounds = _content_range_bounds(response)
        if bounds is not None and bounds[0] == len(partial.data):
            # partial content; append the missing tail to what we already have
            accumulate = True
        else:
            # unsolicited or misaligned range — our offset is unusable for
            # this origin, so start over on the next attempt
            received = len(partial.data)
            response.close()
            partial.clear()
            raise httpx2.ReadError(
                f"Server returned a partial response that does not start at byte {received}; restarting from scratch",
                request=response.request,
            )
    elif (
        response.status_code == 200
        and _accepts_byte_ranges(response)
        and _is_identity_encoded(response)
        and _resume_validator(response) is not None
    ):
        # either no range was sent or the server ignored it; this body is
        # complete. without a strong validator a later range request could
        # silently splice bytes from a different version of the resource,
        # so only validator-bearing responses may be resumed
        partial.reset(response)
        accumulate = True
    elif resuming and response.status_code == 200:
        # the retry delivered a complete replacement body; any partial bytes
        # are superseded
        partial.clear()

    if not accumulate:
        _read_and_release(response)
        return response

    # on a 206 the original response stays the representation of the full
    # body (headers, validator, request); a 200 restart already replaced it.
    # chunks are accumulated exactly once, into the shared partial buffer —
    # per-response copies only happen once the assembled body exists
    offset = len(partial.data)
    try:
        for chunk in response.iter_bytes():
            partial.data.extend(chunk)
    except BaseException:
        # the stream is left open when the body read fails; release the
        # connection before the retry loop takes over
        response.close()
        raise
    delivered_len = len(partial.data) - offset
    bounds = _content_range_bounds(response)
    if resuming and bounds is not None:
        start, end, total = bounds
        if end is not None and delivered_len != end - start + 1:
            # the delivered body contradicts the advertised range extent
            response.close()
            partial.clear()
            raise httpx2.ReadError(
                "Partial response body does not match its Content-Range; restarting from scratch",
                request=response.request,
            )
        if total is None or total != len(partial.data):
            response.close()
            if total is None:
                # the total length is unknown, so completeness can never be
                # proven; restart with a plain full download instead
                partial.clear()
                raise httpx2.ReadError(
                    "Partial response does not report a total length; restarting from scratch",
                    request=response.request,
                )
            # the origin served a satisfying-but-short segment; keep the bytes
            # it did send so the next attempt resumes from the new offset
            raise httpx2.ReadError(
                f"Partial response ended at byte {len(partial.data)} of {total}; resuming",
                request=response.request,
            )
    rebuilt = finish_download(partial, elapsed_from=response)
    # exactly what a non-streaming send() would have left on this response:
    # its own body, so retained references see metadata and content that
    # agree. a fresh 200 restart shares the assembled body zero-copy; a 206
    # keeps its suffix-sized body, not the assembled one
    response._content = rebuilt.content if offset == 0 else rebuilt.content[offset:]
    return rebuilt


def finish_download(partial: _PartialDownload, *, elapsed_from: httpx2.Response) -> httpx2.Response:
    representation = partial.representation
    assert representation is not None
    # hand off the buffer instead of emptying it in place, so the mutable
    # copy stops being reachable the moment the immutable one exists
    buffer = partial.data
    partial.data = bytearray()
    partial.representation = None
    content = bytes(buffer)
    del buffer
    return _reassembled_download_response(representation, content, elapsed_from=elapsed_from)


async def aread_resumable_body(
    response: httpx2.Response,
    partial: _PartialDownload,
) -> httpx2.Response:
    """Async counterpart of `_read_resumable_body`."""
    resuming = bool(partial)
    if resuming and response.status_code == 416:
        total = _range_total_bytes(response)
        representation = partial.representation
        assert representation is not None
        if total is not None and total == len(partial.data):
            # the earlier attempt already received every byte; only the
            # terminating chunks went missing; read the (small) body so a
            # retained reference sees a normally-consumed response
            await _aread_and_release(response)
            return await afinish_download(partial, elapsed_from=response)
        received = len(partial.data)
        await response.aclose()
        partial.clear()
        raise httpx2.ReadError(
            f"Server rejected resuming the download at byte {received} with 416; restarting from scratch",
            request=representation.request,
        )

    accumulate = False
    if resuming and response.status_code == 206:
        bounds = _content_range_bounds(response)
        if bounds is not None and bounds[0] == len(partial.data):
            # partial content; append the missing tail to what we already have
            accumulate = True
        else:
            # unsolicited or misaligned range — our offset is unusable for
            # this origin, so start over on the next attempt
            received = len(partial.data)
            await response.aclose()
            partial.clear()
            raise httpx2.ReadError(
                f"Server returned a partial response that does not start at byte {received}; restarting from scratch",
                request=response.request,
            )
    elif (
        response.status_code == 200
        and _accepts_byte_ranges(response)
        and _is_identity_encoded(response)
        and _resume_validator(response) is not None
    ):
        # either no range was sent or the server ignored it; this body is
        # complete. without a strong validator a later range request could
        # silently splice bytes from a different version of the resource,
        # so only validator-bearing responses may be resumed
        partial.reset(response)
        accumulate = True
    elif resuming and response.status_code == 200:
        # the retry delivered a complete replacement body; any partial bytes
        # are superseded
        partial.clear()

    if not accumulate:
        await _aread_and_release(response)
        return response

    # on a 206 the original response stays the representation of the full
    # body (headers, validator, request); a 200 restart already replaced it.
    # chunks are accumulated exactly once, into the shared partial buffer —
    # per-response copies only happen once the assembled body exists
    offset = len(partial.data)
    try:
        async for chunk in response.aiter_bytes():
            partial.data.extend(chunk)
    except BaseException:
        # includes CancelledError; shield the close so a level-triggered
        # cancellation cannot interrupt the cleanup itself
        with anyio.CancelScope(shield=True):
            await response.aclose()
        raise
    delivered_len = len(partial.data) - offset
    bounds = _content_range_bounds(response)
    if resuming and bounds is not None:
        start, end, total = bounds
        if end is not None and delivered_len != end - start + 1:
            # the delivered body contradicts the advertised range extent
            await response.aclose()
            partial.clear()
            raise httpx2.ReadError(
                "Partial response body does not match its Content-Range; restarting from scratch",
                request=response.request,
            )
        if total is None or total != len(partial.data):
            await response.aclose()
            if total is None:
                # the total length is unknown, so completeness can never be
                # proven; restart with a plain full download instead
                partial.clear()
                raise httpx2.ReadError(
                    "Partial response does not report a total length; restarting from scratch",
                    request=response.request,
                )
            # the origin served a satisfying-but-short segment; keep the bytes
            # it did send so the next attempt resumes from the new offset
            raise httpx2.ReadError(
                f"Partial response ended at byte {len(partial.data)} of {total}; resuming",
                request=response.request,
            )
    rebuilt = await afinish_download(partial, elapsed_from=response)
    # exactly what a non-streaming send() would have left on this response:
    # its own body, so retained references see metadata and content that
    # agree. a fresh 200 restart shares the assembled body zero-copy; a 206
    # keeps its suffix-sized body, not the assembled one
    response._content = rebuilt.content if offset == 0 else rebuilt.content[offset:]
    return rebuilt


async def afinish_download(partial: _PartialDownload, *, elapsed_from: httpx2.Response) -> httpx2.Response:
    representation = partial.representation
    assert representation is not None
    # hand off the buffer instead of emptying it in place, so the mutable
    # copy stops being reachable the moment the immutable one exists
    buffer = partial.data
    partial.data = bytearray()
    partial.representation = None
    content = bytes(buffer)
    del buffer
    return _reassembled_download_response(representation, content, elapsed_from=elapsed_from)
