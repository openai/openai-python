from __future__ import annotations

import pytest

from openai import OpenAI, AsyncOpenAI
from openai._utils import required_args


def test_too_many_positional_params() -> None:
    @required_args(["a"])
    def foo(a: str | None = None) -> str | None:
        return a

    with pytest.raises(TypeError, match=r"foo\(\) takes 1 argument\(s\) but 2 were given"):
        foo("a", "b")  # type: ignore


def test_positional_param() -> None:
    @required_args(["a"])
    def foo(a: str | None = None) -> str | None:
        return a

    assert foo("a") == "a"
    assert foo(None) is None
    assert foo(a="b") == "b"

    with pytest.raises(TypeError, match="Missing required argument: 'a'"):
        foo()


def test_keyword_only_param() -> None:
    @required_args(["a"])
    def foo(*, a: str | None = None) -> str | None:
        return a

    assert foo(a="a") == "a"
    assert foo(a=None) is None
    assert foo(a="b") == "b"

    with pytest.raises(TypeError, match="Missing required argument: 'a'"):
        foo()


def test_multiple_params() -> None:
    @required_args(["a", "b", "c"])
    def foo(a: str = "", *, b: str = "", c: str = "") -> str | None:
        return f"{a} {b} {c}"

    assert foo(a="a", b="b", c="c") == "a b c"

    with pytest.raises(TypeError, match=r"Missing required arguments: 'a', 'b' or 'c'"):
        foo()

    with pytest.raises(TypeError, match=r"Missing required arguments: 'b' or 'c'"):
        foo(a="a")

    with pytest.raises(TypeError, match=r"Missing required arguments: 'a' or 'c'"):
        foo(b="b")

    with pytest.raises(TypeError, match=r"Missing required arguments: 'a' or 'b'"):
        foo(c="c")

    with pytest.raises(TypeError, match=r"Missing required argument: 'a'"):
        foo(b="a", c="c")

    with pytest.raises(TypeError, match=r"Missing required argument: 'b'"):
        foo("a", c="c")


def test_multiple_variants() -> None:
    @required_args(["a"], ["b"])
    def foo(*, a: str | None = None, b: str | None = None) -> str | None:
        return a if a is not None else b

    assert foo(a="foo") == "foo"
    assert foo(b="bar") == "bar"
    assert foo(a=None) is None
    assert foo(b=None) is None

    # TODO: this error message could probably be improved
    with pytest.raises(
        TypeError,
        match=r"Missing required arguments; Expected either \('a'\) or \('b'\) arguments to be given",
    ):
        foo()


def test_multiple_params_multiple_variants() -> None:
    @required_args(["a", "b"], ["c"])
    def foo(*, a: str | None = None, b: str | None = None, c: str | None = None) -> str | None:
        if a is not None:
            return a
        if b is not None:
            return b
        return c

    error_message = r"Missing required arguments; Expected either \('a' and 'b'\) or \('c'\) arguments to be given"

    with pytest.raises(TypeError, match=error_message):
        foo(a="foo")

    with pytest.raises(TypeError, match=error_message):
        foo(b="bar")

    with pytest.raises(TypeError, match=error_message):
        foo()

    assert foo(a=None, b="bar") == "bar"
    assert foo(c=None) is None
    assert foo(c="foo") == "foo"


def test_sync_resource_completions_create_missing_prompt(client: OpenAI) -> None:
    with pytest.raises(TypeError, match=r"Expected either .*'model'.*'prompt'.*"):
        client.completions.create(model="gpt-3.5-turbo-instruct")  # type: ignore[call-arg]


def test_sync_resource_images_edit_missing_prompt(client: OpenAI) -> None:
    with pytest.raises(TypeError, match=r"Expected either .*'image'.*'prompt'.*"):
        client.images.edit(image=b"Example data")  # type: ignore[call-arg]


def test_sync_resource_audio_transcriptions_create_missing_model(client: OpenAI) -> None:
    with pytest.raises(TypeError, match=r"Expected either .*'file'.*'model'.*"):
        client.audio.transcriptions.create(file=b"Example data")  # type: ignore[call-arg]


def test_sync_resource_beta_threads_create_and_run_missing_assistant_id(client: OpenAI) -> None:
    error_message = r"Missing required arguments; Expected either \('assistant_id'\) or \('assistant_id' and 'stream'\) arguments to be given"

    with pytest.warns(DeprecationWarning, match="The Assistants API is deprecated"):
        with pytest.raises(TypeError, match=error_message):
            client.beta.threads.create_and_run()  # type: ignore[call-arg]


def test_sync_resource_beta_threads_runs_create_missing_assistant_id(client: OpenAI) -> None:
    error_message = r"Missing required arguments; Expected either \('assistant_id'\) or \('assistant_id' and 'stream'\) arguments to be given"

    with pytest.warns(DeprecationWarning, match="The Assistants API is deprecated"):
        with pytest.raises(TypeError, match=error_message):
            client.beta.threads.runs.create("thread_123")  # type: ignore[call-arg]


async def test_async_resource_chat_completions_create_missing_messages(async_client: AsyncOpenAI) -> None:
    with pytest.raises(TypeError, match=r"Expected either .*'messages'.*'model'.*"):
        async_client.chat.completions.create(model="gpt-5.4")  # type: ignore[call-arg]


async def test_async_resource_images_generate_missing_prompt(async_client: AsyncOpenAI) -> None:
    with pytest.raises(TypeError, match=r"Expected either .*'prompt'.*"):
        async_client.images.generate()  # type: ignore[call-arg]


async def test_async_resource_beta_threads_runs_submit_tool_outputs_missing_tool_outputs(
    async_client: AsyncOpenAI,
) -> None:
    error_message = r"Missing required arguments; Expected either \('thread_id' and 'tool_outputs'\) or \('thread_id', 'stream' and 'tool_outputs'\) arguments to be given"

    with pytest.warns(DeprecationWarning, match="The Assistants API is deprecated"):
        with pytest.raises(TypeError, match=error_message):
            async_client.beta.threads.runs.submit_tool_outputs("run_123", thread_id="thread_123")  # type: ignore[call-arg]
