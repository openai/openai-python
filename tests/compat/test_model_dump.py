import pydantic

from openai._compat import model_dump


class SimpleModel(pydantic.BaseModel):
    foo: str = "bar"


def test_model_dump_by_alias_none() -> None:
    """Regression test for #2921: by_alias=None should not raise TypeError."""
    result = model_dump(SimpleModel(), by_alias=None)
    assert result == {"foo": "bar"}


def test_model_dump_by_alias_true() -> None:
    result = model_dump(SimpleModel(), by_alias=True)
    assert result == {"foo": "bar"}


def test_model_dump_by_alias_false() -> None:
    result = model_dump(SimpleModel(), by_alias=False)
    assert result == {"foo": "bar"}
