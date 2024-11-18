from __future__ import annotations

import sys
import asyncio
import functools
import contextvars
from typing import Any, TypeVar, Callable, Awaitable
from typing_extensions import ParamSpec

T_Retval = TypeVar("T_Retval")
T_ParamSpec = ParamSpec("T_ParamSpec")


if sys.version_info >= (3, 9):
    to_thread = asyncio.to_thread
else:
    # backport of https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread
    # for Python 3.8 support
    async def to_thread(
        func: Callable[T_ParamSpec, T_Retval], /, *args: T_ParamSpec.args, **kwargs: T_ParamSpec.kwargs
    ) -> Any:
        """Asynchronously run function *func* in a separate thread.

        Any *args and **kwargs supplied for this function are directly passed
        to *func*. Also, the current :class:`contextvars.Context` is propagated,
        allowing context variables from the main thread to be accessed in the
        separate thread.

        Returns a coroutine that can be awaited to get the eventual result of *func*.
        """
        loop = asyncio.events.get_running_loop()
        ctx = contextvars.copy_context()
        func_call = functools.partial(ctx.run, func, *args, **kwargs)
        return await loop.run_in_executor(None, func_call)


# inspired by `asyncer`, https://github.com/tiangolo/asyncer
def asyncify(function: Callable[T_ParamSpec, T_Retval]) -> Callable[T_ParamSpec, Awaitable[T_Retval]]:
    """
    Take a blocking function and create an async one that receives the same
    positional and keyword arguments. For python version 3.9 and above, it uses
    asyncio.to_thread to run the function in a separate thread. For python version
    3.8, it uses locally defined copy of the asyncio.to_thread function which was
    introduced in python 3.9.

    Usage:

    ```python
    def blocking_func(arg1, arg2, kwarg1=None):
        # blocking code
        return result


    result = asyncify(blocking_function)(arg1, arg2, kwarg1=value1)
    ```

    ## Arguments

    `function`: a blocking regular callable (e.g. a function)

    ## Return

    An async function that takes the same positional and keyword arguments as the
    original one, that when called runs the same original function in a thread worker
    and returns the result.
    """

    async def wrapper(*args: T_ParamSpec.args, **kwargs: T_ParamSpec.kwargs) -> T_Retval:
        return await to_thread(function, *args, **kwargs)

    return wrapper
