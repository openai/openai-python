from __future__ import annotations

import pytest

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

    error_message = r"Missing required arguments.*"

    with pytest.raises(TypeError, match=error_message):
        foo()

    with pytest.raises(TypeError, match=error_message):
        foo(a="a")

    with pytest.raises(TypeError, match=error_message):
        foo(b="b")

    with pytest.raises(TypeError, match=error_message):
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
