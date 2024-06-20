from __future__ import annotations

import inspect
from typing import Any, Callable

import pytest

from openai import OpenAI, AsyncOpenAI


def assert_signatures_in_sync(
    source_func: Callable[..., Any],
    check_func: Callable[..., Any],
    *,
    exclude_params: set[str] = set(),
) -> None:
    check_sig = inspect.signature(check_func)
    source_sig = inspect.signature(source_func)

    errors: list[str] = []

    for name, generated_param in source_sig.parameters.items():
        if name in exclude_params:
            continue

        custom_param = check_sig.parameters.get(name)
        if not custom_param:
            errors.append(f"the `{name}` param is missing")
            continue

        if custom_param.annotation != generated_param.annotation:
            errors.append(
                f"types for the `{name}` param are do not match; generated={repr(generated_param.annotation)} custom={repr(generated_param.annotation)}"
            )
            continue

    if errors:
        raise AssertionError(f"{len(errors)} errors encountered when comparing signatures:\n\n" + "\n\n".join(errors))


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_create_and_run_poll_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.beta.threads.create_and_run,
        checking_client.beta.threads.create_and_run_poll,
        exclude_params={"stream"},
    )

@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_create_and_run_stream_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.beta.threads.create_and_run,
        checking_client.beta.threads.create_and_run_stream,
        exclude_params={"stream"},
    )
