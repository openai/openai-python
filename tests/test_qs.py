from typing import Any, cast
from functools import partial
from urllib.parse import unquote

import pytest

from openai._qs import Querystring, stringify
from openai._types import ArrayFormat


def test_empty() -> None:
    assert stringify({}) == ""
    assert stringify({"a": {}}) == ""
    assert stringify({"a": {"b": {"c": {}}}}) == ""


def test_basic() -> None:
    assert stringify({"a": 1}) == "a=1"
    assert stringify({"a": "b"}) == "a=b"
    assert stringify({"a": True}) == "a=true"
    assert stringify({"a": False}) == "a=false"
    assert stringify({"a": 1.23456}) == "a=1.23456"
    assert stringify({"a": None}) == ""


@pytest.mark.parametrize("method", ["class", "function"])
def test_nested_dotted(method: str) -> None:
    if method == "class":
        serialise = Querystring(nested_format="dots").stringify
    else:
        serialise = partial(stringify, nested_format="dots")

    assert unquote(serialise({"a": {"b": "c"}})) == "a.b=c"
    assert unquote(serialise({"a": {"b": "c", "d": "e", "f": "g"}})) == "a.b=c&a.d=e&a.f=g"
    assert unquote(serialise({"a": {"b": {"c": {"d": "e"}}}})) == "a.b.c.d=e"
    assert unquote(serialise({"a": {"b": True}})) == "a.b=true"


def test_nested_brackets() -> None:
    assert unquote(stringify({"a": {"b": "c"}})) == "a[b]=c"
    assert unquote(stringify({"a": {"b": "c", "d": "e", "f": "g"}})) == "a[b]=c&a[d]=e&a[f]=g"
    assert unquote(stringify({"a": {"b": {"c": {"d": "e"}}}})) == "a[b][c][d]=e"
    assert unquote(stringify({"a": {"b": True}})) == "a[b]=true"


@pytest.mark.parametrize("method", ["class", "function"])
def test_array_comma(method: str) -> None:
    if method == "class":
        serialise = Querystring(array_format="comma").stringify
    else:
        serialise = partial(stringify, array_format="comma")

    assert unquote(serialise({"in": ["foo", "bar"]})) == "in=foo,bar"
    assert unquote(serialise({"a": {"b": [True, False]}})) == "a[b]=true,false"
    assert unquote(serialise({"a": {"b": [True, False, None, True]}})) == "a[b]=true,false,true"
    assert unquote(serialise({"filter": []})) == ""
    assert unquote(serialise({"filter": [None]})) == ""
    assert unquote(serialise({"filter": [""]})) == "filter="
    assert unquote(serialise({"filter": [None, "active"]})) == "filter=active"


@pytest.mark.parametrize("array_format", ["comma", "repeat", "indices", "brackets"])
def test_empty_array_omits_parameter(array_format: ArrayFormat) -> None:
    # Non-empty output remains format-specific; only the empty outcome is shared.
    assert stringify({"filter": []}, array_format=array_format) == ""
    assert stringify({"filter": [None]}, array_format=array_format) == ""


def test_array_repeat() -> None:
    assert unquote(stringify({"in": ["foo", "bar"]})) == "in=foo&in=bar"
    assert unquote(stringify({"a": {"b": [True, False]}})) == "a[b]=true&a[b]=false"
    assert unquote(stringify({"a": {"b": [True, False, None, True]}})) == "a[b]=true&a[b]=false&a[b]=true"
    assert unquote(stringify({"in": ["foo", {"b": {"c": ["d", "e"]}}]})) == "in=foo&in[b][c]=d&in[b][c]=e"


@pytest.mark.parametrize("method", ["class", "function"])
def test_array_brackets(method: str) -> None:
    if method == "class":
        serialise = Querystring(array_format="brackets").stringify
    else:
        serialise = partial(stringify, array_format="brackets")

    assert unquote(serialise({"in": ["foo", "bar"]})) == "in[]=foo&in[]=bar"
    assert unquote(serialise({"a": {"b": [True, False]}})) == "a[b][]=true&a[b][]=false"
    assert unquote(serialise({"a": {"b": [True, False, None, True]}})) == "a[b][]=true&a[b][]=false&a[b][]=true"


def test_unknown_array_format() -> None:
    with pytest.raises(NotImplementedError, match="Unknown array_format value: foo, choose from comma, repeat"):
        stringify({"a": ["foo", "bar"]}, array_format=cast(Any, "foo"))


@pytest.mark.parametrize("nested_format", ["brackets", "dots"])
def test_empty_string_metadata_filter(nested_format: str) -> None:
    key = "metadata[state]" if nested_format == "brackets" else "metadata.state"
    assert unquote(stringify({"metadata": {"state": ""}}, nested_format=cast(Any, nested_format))) == f"{key}="


def test_empty_string_and_none_are_distinct() -> None:
    assert stringify({"empty": "", "absent": None}) == "empty="
    assert unquote(stringify({"metadata": {"state": "", "absent": None}})) == "metadata[state]="
