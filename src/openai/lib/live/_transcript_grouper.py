from __future__ import annotations

import time
import asyncio
import inspect
import threading
from types import TracebackType
from typing import TypeVar, Callable, Sequence, Awaitable
from collections import deque
from dataclasses import dataclass
from typing_extensions import Self, Protocol, override

from ._types import GroupingUpdate, TranscriptGrouperOptions
from ._listeners import TranscriptListeners
from ...types.live import ServerEvent
from ..._exceptions import OpenAIError
from ._transcript_state import TranscriptState

_ReturnT = TypeVar("_ReturnT")


class _Timer(Protocol):
    def cancel(self) -> None: ...


@dataclass
class _DispatchRun:
    task: asyncio.Task[None] | None = None
    waiters: int = 0
    observed: bool = False


class _BaseTranscriptGrouper(TranscriptListeners[_ReturnT]):
    def __init__(self, options: TranscriptGrouperOptions) -> None:
        super().__init__()
        self._state = TranscriptState(options, self._now)
        self._updates: deque[GroupingUpdate] = deque()
        self._timer: _Timer | None = None
        self._timer_generation = 0

    def _now(self) -> float:
        return time.monotonic() * 1000

    def _clear_timer(self) -> None:
        self._timer_generation += 1
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def _schedule(self) -> None:
        self._clear_timer()
        delay = self._state.delay()
        if delay is not None:
            generation = self._timer_generation
            self._timer = self._call_later(delay, lambda: self._timer_fired(generation))

    def _call_later(self, delay_ms: int, callback: Callable[[], None]) -> _Timer:
        raise NotImplementedError

    def _timer_fired(self, generation: int) -> None:
        raise NotImplementedError


def _options(
    min_turn_separation_ms: float | None,
    assistant_silence_ms: float | None,
    backchannel_max_duration_ms: float | None,
    backchannel_isolation_ms: float | None,
    additional_acknowledgments: Sequence[str] | None,
) -> TranscriptGrouperOptions:
    return TranscriptGrouperOptions(
        500 if min_turn_separation_ms is None else min_turn_separation_ms,
        2000 if assistant_silence_ms is None else assistant_silence_ms,
        1000 if backchannel_max_duration_ms is None else backchannel_max_duration_ms,
        2000 if backchannel_isolation_ms is None else backchannel_isolation_ms,
        tuple(additional_acknowledgments or ()),
    )


class TranscriptGrouper(_BaseTranscriptGrouper[None]):
    """Group public Live transcript events into immutable display segments.

    This is the TypeScript SDK's speaker/backchannel policy: only transcript
    additions and session.closed are consumed. It is not VAD, playback tracking,
    or a lossless transcript; brief overlapping acknowledgments may be suppressed.
    Set backchannel_max_duration_ms=0 to disable suppression.
    additional_acknowledgments extends the built-in phrases using the same timing
    thresholds. Phrases are copied at construction and normalized like transcript
    text: case, hyphens, whitespace, and surrounding punctuation are normalized.

    Use one instance per session. Call close() on disconnect or use a with block;
    the grouper never owns, closes or reconnects your transport. Delayed delivery
    can change grouping because monotonic local time supplies inactivity fallback.

    Callbacks are serialized and run outside the state lock. A timer-triggered
    callback may run on a daemon timer thread. Callback exceptions propagate to
    push/close callers, or to threading.excepthook for timer-triggered callbacks.
    """

    def __init__(
        self,
        *,
        min_turn_separation_ms: float | None = None,
        assistant_silence_ms: float | None = None,
        backchannel_max_duration_ms: float | None = None,
        backchannel_isolation_ms: float | None = None,
        additional_acknowledgments: Sequence[str] | None = None,
    ) -> None:
        super().__init__(
            _options(
                min_turn_separation_ms,
                assistant_silence_ms,
                backchannel_max_duration_ms,
                backchannel_isolation_ms,
                additional_acknowledgments,
            )
        )
        self._lock = threading.Lock()
        self._dispatching = False

    def push(self, event: ServerEvent) -> None:
        """Consume one typed Live event; duplicates and unrelated events are ignored.

        Invalid transcript fields or use after close raise OpenAIError before
        changing state. Empty text does not restart inactivity.
        """
        with self._lock:
            updates = self._state.push(event)
            if updates is None:
                return
            self._updates.extend(updates)
            self._schedule()
        self._dispatch()

    def close(self) -> None:
        """Flush/finalize once and cancel timers, without closing the transport.

        Already-running callbacks finish in order, including when close is called
        from a callback. Further push calls fail.
        """
        with self._lock:
            self._updates.extend(self._state.finish("manual"))
            self._clear_timer()
        self._dispatch()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None
    ) -> None:
        self.close()

    @override
    def _call_later(self, delay_ms: int, callback: Callable[[], None]) -> _Timer:
        timer = threading.Timer(delay_ms / 1000, callback)
        timer.daemon = True
        timer.start()
        return timer

    @override
    def _timer_fired(self, generation: int) -> None:
        with self._lock:
            if generation != self._timer_generation or self._state.closed:
                return
            self._timer = None
            self._updates.extend(self._state.tick())
            self._schedule()
        self._dispatch()

    def _dispatch(self) -> None:
        with self._lock:
            if self._dispatching:
                return
            self._dispatching = True
        try:
            while True:
                with self._lock:
                    if not self._updates:
                        self._dispatching = False
                        return
                    update = self._updates.popleft()
                for handler in self._handlers(update):
                    handler(update)
        except BaseException:
            with self._lock:
                self._dispatching = False
            raise


class AsyncTranscriptGrouper(_BaseTranscriptGrouper[None | Awaitable[None]]):
    """Asyncio counterpart of TranscriptGrouper, sharing exactly the same policy.

    additional_acknowledgments extends the built-in phrases with the same
    normalization and timing thresholds as TranscriptGrouper.

    Use async with, await push(event), and await close(). Register synchronous
    or asynchronous callbacks with on/once. Handlers run sequentially on the
    owning event loop; timer callbacks never run on a worker thread. Exceptions
    from timer-triggered handlers go to the event loop's exception handler.
    """

    def __init__(
        self,
        *,
        min_turn_separation_ms: float | None = None,
        assistant_silence_ms: float | None = None,
        backchannel_max_duration_ms: float | None = None,
        backchannel_isolation_ms: float | None = None,
        additional_acknowledgments: Sequence[str] | None = None,
    ) -> None:
        super().__init__(
            _options(
                min_turn_separation_ms,
                assistant_silence_ms,
                backchannel_max_duration_ms,
                backchannel_isolation_ms,
                additional_acknowledgments,
            )
        )
        self._loop: asyncio.AbstractEventLoop | None = None
        self._dispatch_run: _DispatchRun | None = None

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        loop = asyncio.get_running_loop()
        if self._loop is None:
            self._loop = loop
        elif self._loop is not loop:
            raise OpenAIError("The async transcript grouper must be used on its owning event loop")
        return loop

    async def push(self, event: ServerEvent) -> None:
        """Consume one event and dispatch its updates; await async handlers in order."""
        self._get_loop()
        updates = self._state.push(event)
        if updates is None:
            return
        self._updates.extend(updates)
        self._schedule()
        await self._dispatch()

    async def close(self) -> None:
        """Finalize the projection and cancel timers. Idempotent; owns no transport."""
        self._get_loop()
        self._updates.extend(self._state.finish("manual"))
        self._clear_timer()
        await self._dispatch()

    async def __aenter__(self) -> Self:
        self._get_loop()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None
    ) -> None:
        await self.close()

    @override
    def _call_later(self, delay_ms: int, callback: Callable[[], None]) -> _Timer:
        return self._get_loop().call_later(delay_ms / 1000, callback)

    @override
    def _timer_fired(self, generation: int) -> None:
        if generation != self._timer_generation or self._state.closed:
            return
        self._timer = None
        self._updates.extend(self._state.tick())
        self._schedule()
        self._start_dispatch()

    def _dispatch_finished(self, run: _DispatchRun, task: asyncio.Task[None]) -> None:
        if self._dispatch_run is run:
            self._dispatch_run = None
        if task.cancelled():
            return
        error = task.exception()
        if error is not None and not run.waiters and not run.observed:
            self._get_loop().call_exception_handler(
                {"message": "Live transcript callback failed", "exception": error, "task": task}
            )

    def _start_dispatch(self) -> _DispatchRun | None:
        run = self._dispatch_run
        if run is not None and run.task is not None and not run.task.done():
            return run
        if not self._updates:
            return None
        run = _DispatchRun()
        self._dispatch_run = run
        run.task = self._get_loop().create_task(self._dispatch_updates(run))
        run.task.add_done_callback(lambda task: self._dispatch_finished(run, task))
        return run

    async def _dispatch(self) -> None:
        run = self._dispatch_run
        if run is not None and run.task is asyncio.current_task():
            return
        run = self._start_dispatch()
        if run is None:
            return
        assert run.task is not None
        run.waiters += 1
        try:
            # A cancelled push/close caller must not interrupt an event halfway
            # through its listeners, especially once session closure is committed.
            await asyncio.shield(run.task)
        except asyncio.CancelledError:
            raise
        except BaseException:
            run.observed = True
            raise
        else:
            run.observed = True
        finally:
            run.waiters -= 1

    async def _dispatch_updates(self, run: _DispatchRun) -> None:
        # Set ownership before handlers run, including with an eager task factory.
        run.task = asyncio.current_task()
        while self._updates:
            update = self._updates.popleft()
            for handler in self._handlers(update):
                result = handler(update)
                if inspect.isawaitable(result):
                    await result
