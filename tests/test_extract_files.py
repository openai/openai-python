from __future__ import annotations

from typing import Sequence

import pytest

from openai._types import FileTypes
from openai._utils import extract_files


def test_removes_files_from_input() -> None:
    query = {"foo": "bar"}
    assert extract_files(query, paths=[]) == []
    assert query == {"foo": "bar"}

    query2 = {"foo": b"Bar", "hello": "world"}
    assert extract_files(query2, paths=[["foo"]]) == [("foo", b"Bar")]
    assert query2 == {"hello": "world"}

    query3 = {"foo": {"foo": {"bar": b"Bar"}}, "hello": "world"}
    assert extract_files(query3, paths=[["foo", "foo", "bar"]]) == [("foo[foo][bar]", b"Bar")]
    assert query3 == {"foo": {"foo": {}}, "hello": "world"}

    query4 = {"foo": {"bar": b"Bar", "baz": "foo"}, "hello": "world"}
    assert extract_files(query4, paths=[["foo", "bar"]]) == [("foo[bar]", b"Bar")]
    assert query4 == {"hello": "world", "foo": {"baz": "foo"}}


def test_multiple_files() -> None:
    query = {"documents": [{"file": b"My first file"}, {"file": b"My second file"}]}
    assert extract_files(query, paths=[["documents", "<array>", "file"]]) == [
        ("documents[][file]", b"My first file"),
        ("documents[][file]", b"My second file"),
    ]
    assert query == {"documents": [{}, {}]}


@pytest.mark.parametrize(
    "query,paths,expected",
    [
        [
            {"foo": {"bar": "baz"}},
            [["foo", "<array>", "bar"]],
            [],
        ],
        [
            {"foo": ["bar", "baz"]},
            [["foo", "bar"]],
            [],
        ],
        [
            {"foo": {"bar": "baz"}},
            [["foo", "foo"]],
            [],
        ],
    ],
    ids=["dict expecting array", "array expecting dict", "unknown keys"],
)
def test_ignores_incorrect_paths(
    query: dict[str, object],
    paths: Sequence[Sequence[str]],
    expected: list[tuple[str, FileTypes]],
) -> None:
    assert extract_files(query, paths=paths) == expected
