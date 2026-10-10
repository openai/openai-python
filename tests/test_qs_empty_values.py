from urllib.parse import unquote

from openai._qs import stringify


def test_empty_string_scalar_is_preserved() -> None:
    assert stringify({"filter": ""}) == "filter="


def test_none_scalar_is_still_omitted() -> None:
    assert stringify({"filter": None}) == ""


def test_nested_empty_string_is_preserved() -> None:
    assert unquote(stringify({"filter": {"name": ""}})) == "filter[name]="


def test_empty_string_in_repeat_array_is_preserved() -> None:
    assert stringify({"filter": ["", "active"]}) == "filter=&filter=active"
