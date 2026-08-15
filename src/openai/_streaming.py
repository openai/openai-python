# Note: initially copied from https://github.com/florimondmanca/httpx-sse/blob/master/src/httpx_sse/_decoders.py
from __future__ import annotations

import json
import inspect
from types import TracebackType
from typing import TYPE_CHECKING, Any, Generic, TypeVar, Iterator, Optional, AsyncIterator, cast
from typing_extensions import Self, Protocol, TypeGuard, override, get_origin, runtime_checkable

import httpx

from ._utils import is_mapping, extract_type_var_from_base
from ._exceptions import APIError

if TYPE_CHECKING:
    from ._client import OpenAI, AsyncOpenAI
    from ._models import FinalRequestOptions


_T = TypeVar("_T")


class Stream(Generic[_T]):
    """Provides the core interface to iterate over a synchronous stream response."""

    response: httpx.Response
    _options: Optional[FinalRequestOptions] = None
    _decoder: SSEBytesDecoder

    def __init__(
        self,
        *,
        cast_to: type[_T],
        response: httpx.Response,
        client: OpenAI,
        options: Optional[FinalRequestOptions] = None,
    ) -> None:
        self.response = response
        self._cast_to = cast_to
        self._client = client
        self._options = options
        self._decoder = client._make_sse_decoder()
        self._iterator = self.__stream__()

    def __next__(self) -> _T:
        return self._iterator.__next__()

    def __iter__(self) -> Iterator[_T]:
        for item in self._iterator:
            yield item

    def _iter_events(self) -> Iterator[ServerSentEvent]:
        yield from self._decoder.iter_bytes(self.response.iter_bytes())

    def __stream__(self) -> Iterator[_T]:
        cast_to = cast(Any, self._cast_to)
        response = self.response
        process_data = self._client._process_response_data
        iterator = self._iter_events()

        try:
            for sse in iterator:
                if sse.data.startswith("[DONE]"):
                    break

                # we have to special case the Assistants `thread.` events since we won't have an "event" key in the data
                if sse.event and sse.event.startswith("thread."):
                    data = sse.json()

                    if sse.event == "error" and is_mapping(data) and data.get("error"):
                        message = None
                        error = data.get("error")
                        if is_mapping(error):
                            message = error.get("message")
                        if not message or not isinstance(message, str):
                            message = "An error occurred during streaming"

                        raise APIError(
                            message=message,
                            request=self.response.request,
                            body=data["error"],
                        )

                    yield process_data(data={"data": data, "event": sse.event}, cast_to=cast_to, response=response)
                else:
                    data = sse.json()
                    if is_mapping(data) and data.get("error"):
                        message = None
                        error = data.get("error")
                        if is_mapping(error):
                            message = error.get("message")
                        if not message or not isinstance(message, str):
                            message = "An error occurred during streaming"

                        raise APIError(
                            message=message,
                            request=self.response.request,
                            body=data["error"],
                        )

                    yield process_data(
                        data={"data": data, "event": sse.event}
                        if self._options is not None and self._options.synthesize_event_and_data
                        else data,
                        cast_to=cast_to,
                        response=response,
                    )
        finally:
            # Ensure the response is closed even if the consumer doesn't read all data
            response.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        """
        Close the response and release the connection.

        Automatically called if the response body is read to completion.
        Ensures response resources and connection streams are safely released on stream termination.
        """
        self.response.close()
