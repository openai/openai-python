from __future__ import annotations

from typing import Generic, TypeVar, cast

from openai._utils import extract_type_var_from_base

_T = TypeVar("_T")
_T2 = TypeVar("_T2")
_T3 = TypeVar("_T3")


class BaseGeneric(Generic[_T]): ...


class SubclassGeneric(BaseGeneric[_T]): ...


class BaseGenericMultipleTypeArgs(Generic[_T, _T2, _T3]): ...


class SubclassGenericMultipleTypeArgs(BaseGenericMultipleTypeArgs[_T, _T2, _T3]): ...


class SubclassDifferentOrderGenericMultipleTypeArgs(BaseGenericMultipleTypeArgs[_T2, _T, _T3]): ...


def test_extract_type_var() -> None:
    assert (
        extract_type_var_from_base(
            BaseGeneric[int],
            index=0,
            generic_bases=cast("tuple[type, ...]", (BaseGeneric,)),
        )
        == int
    )


def test_extract_type_var_generic_subclass() -> None:
    assert (
        extract_type_var_from_base(
            SubclassGeneric[int],
            index=0,
            generic_bases=cast("tuple[type, ...]", (BaseGeneric,)),
        )
        == int
    )


def test_extract_type_var_multiple() -> None:
    typ = BaseGenericMultipleTypeArgs[int, str, None]

    generic_bases = cast("tuple[type, ...]", (BaseGenericMultipleTypeArgs,))
    assert extract_type_var_from_base(typ, index=0, generic_bases=generic_bases) == int
    assert extract_type_var_from_base(typ, index=1, generic_bases=generic_bases) == str
    assert extract_type_var_from_base(typ, index=2, generic_bases=generic_bases) == type(None)


def test_extract_type_var_generic_subclass_multiple() -> None:
    typ = SubclassGenericMultipleTypeArgs[int, str, None]

    generic_bases = cast("tuple[type, ...]", (BaseGenericMultipleTypeArgs,))
    assert extract_type_var_from_base(typ, index=0, generic_bases=generic_bases) == int
    assert extract_type_var_from_base(typ, index=1, generic_bases=generic_bases) == str
    assert extract_type_var_from_base(typ, index=2, generic_bases=generic_bases) == type(None)


def test_extract_type_var_generic_subclass_different_ordering_multiple() -> None:
    typ = SubclassDifferentOrderGenericMultipleTypeArgs[int, str, None]

    generic_bases = cast("tuple[type, ...]", (BaseGenericMultipleTypeArgs,))
    assert extract_type_var_from_base(typ, index=0, generic_bases=generic_bases) == int
    assert extract_type_var_from_base(typ, index=1, generic_bases=generic_bases) == str
    assert extract_type_var_from_base(typ, index=2, generic_bases=generic_bases) == type(None)
