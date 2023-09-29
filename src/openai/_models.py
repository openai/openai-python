from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Type, Union, Generic, TypeVar, cast
from datetime import date, datetime
from typing_extensions import ClassVar, Protocol, final, runtime_checkable

import pydantic
import pydantic.generics
from pydantic import Extra
from pydantic.fields import FieldInfo

from ._types import (
    Body,
    Query,
    ModelT,
    Headers,
    Timeout,
    NotGiven,
    AnyMapping,
    RequestFiles,
)
from ._utils import is_list, is_mapping, parse_date, parse_datetime, strip_not_given
from ._compat import PYDANTIC_V2, ConfigDict
from ._compat import GenericModel as BaseGenericModel
from ._compat import (
    get_args,
    is_union,
    parse_obj,
    get_origin,
    is_literal_type,
    get_model_config,
    get_model_fields,
    field_get_default,
)

__all__ = ["BaseModel", "GenericModel"]

_T = TypeVar("_T")


@runtime_checkable
class _ConfigProtocol(Protocol):
    allow_population_by_field_name: bool


class BaseModel(pydantic.BaseModel):
    if PYDANTIC_V2:
        model_config: ClassVar[ConfigDict] = ConfigDict(extra="allow")
    else:

        @property
        def model_fields_set(self) -> set[str]:
            # a forwards-compat shim for pydantic v2
            return self.__fields_set__  # type: ignore

        class Config(pydantic.BaseConfig):  # pyright: ignore[reportDeprecated]
            extra: Any = Extra.allow  # type: ignore

    def __str__(self) -> str:
        # mypy complains about an invalid self arg
        return f'{self.__repr_name__()}({self.__repr_str__(", ")})'  # type: ignore[misc]

    # Override the 'construct' method in a way that supports recursive parsing without validation.
    # Based on https://github.com/samuelcolvin/pydantic/issues/1168#issuecomment-817742836.
    @classmethod
    def construct(
        cls: Type[ModelT],
        _fields_set: set[str] | None = None,
        **values: object,
    ) -> ModelT:
        m = cls.__new__(cls)
        fields_values: dict[str, object] = {}

        config = get_model_config(cls)
        populate_by_name = (
            config.allow_population_by_field_name
            if isinstance(config, _ConfigProtocol)
            else config.get("populate_by_name")
        )

        if _fields_set is None:
            _fields_set = set()

        model_fields = get_model_fields(cls)
        for name, field in model_fields.items():
            key = field.alias
            if key is None or (key not in values and populate_by_name):
                key = name

            if key in values:
                fields_values[name] = _construct_field(value=values[key], field=field, key=key)
                _fields_set.add(name)
            else:
                fields_values[name] = field_get_default(field)

        _extra = {}
        for key, value in values.items():
            if key not in model_fields:
                if PYDANTIC_V2:
                    _extra[key] = value
                else:
                    fields_values[key] = value

        object.__setattr__(m, "__dict__", fields_values)

        if PYDANTIC_V2:
            # these properties are copied from Pydantic's `model_construct()` method
            object.__setattr__(m, "__pydantic_private__", None)
            object.__setattr__(m, "__pydantic_extra__", _extra)
            object.__setattr__(m, "__pydantic_fields_set__", _fields_set)
        else:
            # init_private_attributes() does not exist in v2
            m._init_private_attributes()  # type: ignore

            # copied from Pydantic v1's `construct()` method
            object.__setattr__(m, "__fields_set__", _fields_set)

        return m

    if not TYPE_CHECKING:
        # type checkers incorrectly complain about this assignment
        # because the type signatures are technically different
        # although not in practice
        model_construct = construct


def _construct_field(value: object, field: FieldInfo, key: str) -> object:
    if value is None:
        return field_get_default(field)

    if PYDANTIC_V2:
        type_ = field.annotation
    else:
        type_ = cast(type, field.outer_type_)  # type: ignore

    if type_ is None:
        raise RuntimeError(f"Unexpected field type is None for {key}")

    return construct_type(value=value, type_=type_)


def construct_type(*, value: object, type_: type) -> object:
    """Loose coercion to the expected type with construction of nested values.

    If the given value does not match the expected type then it is returned as-is.
    """

    # we need to use the origin class for any types that are subscripted generics
    # e.g. Dict[str, object]
    origin = get_origin(type_) or type_
    args = get_args(type_)

    if is_union(origin):
        try:
            return validate_type(type_=type_, value=value)
        except Exception:
            pass

        # if the data is not valid, use the first variant that doesn't fail while deserializing
        for variant in args:
            try:
                return construct_type(value=value, type_=variant)
            except Exception:
                continue

        raise RuntimeError(f"Could not convert data into a valid instance of {type_}")

    if origin == dict:
        if not is_mapping(value):
            return value

        _, items_type = get_args(type_)  # Dict[_, items_type]
        return {key: construct_type(value=item, type_=items_type) for key, item in value.items()}

    if not is_literal_type(type_) and (issubclass(origin, BaseModel) or issubclass(origin, GenericModel)):
        if is_list(value):
            return [cast(Any, type_).construct(**entry) if is_mapping(entry) else entry for entry in value]

        if is_mapping(value):
            if issubclass(type_, BaseModel):
                return type_.construct(**value)  # type: ignore[arg-type]

            return cast(Any, type_).construct(**value)

    if origin == list:
        if not is_list(value):
            return value

        inner_type = args[0]  # List[inner_type]
        return [construct_type(value=entry, type_=inner_type) for entry in value]

    if origin == float:
        try:
            return float(cast(Any, value))
        except Exception:
            return value

    if origin == int:
        try:
            return int(cast(Any, value))
        except Exception:
            return value

    if type_ == datetime:
        try:
            return parse_datetime(value)  # type: ignore
        except Exception:
            return value

    if type_ == date:
        try:
            return parse_date(value)  # type: ignore
        except Exception:
            return value

    return value


def validate_type(*, type_: type[_T], value: object) -> _T:
    """Strict validation that the given value matches the expected type"""
    if inspect.isclass(type_) and issubclass(type_, pydantic.BaseModel):
        return cast(_T, parse_obj(type_, value))

    return cast(_T, _validate_non_model_type(type_=type_, value=value))


# our use of subclasssing here causes weirdness for type checkers,
# so we just pretend that we don't subclass
if TYPE_CHECKING:
    GenericModel = BaseModel
else:

    class GenericModel(BaseGenericModel, BaseModel):
        pass


if PYDANTIC_V2:
    from pydantic import TypeAdapter

    def _validate_non_model_type(*, type_: type[_T], value: object) -> _T:
        return TypeAdapter(type_).validate_python(value)

elif not TYPE_CHECKING:  # TODO: condition is weird

    class RootModel(GenericModel, Generic[_T]):
        """Used as a placeholder to easily convert runtime types to a Pydantic format
        to provide validation.

        For example:
        ```py
        validated = RootModel[int](__root__='5').__root__
        # validated: 5
        ```
        """

        __root__: _T

    def _validate_non_model_type(*, type_: type[_T], value: object) -> _T:
        model = _create_pydantic_model(type_).validate(value)
        return cast(_T, model.__root__)

    def _create_pydantic_model(type_: _T) -> Type[RootModel[_T]]:
        return RootModel[type_]  # type: ignore


@final
class FinalRequestOptions(pydantic.BaseModel):
    method: str
    url: str
    params: Query = {}
    headers: Union[Headers, NotGiven] = NotGiven()
    max_retries: Union[int, NotGiven] = NotGiven()
    timeout: Union[float, Timeout, None, NotGiven] = NotGiven()
    files: Union[RequestFiles, None] = None
    idempotency_key: Union[str, None] = None

    # It should be noted that we cannot use `json` here as that would override
    # a BaseModel method in an incompatible fashion.
    json_data: Union[Body, None] = None
    extra_json: Union[AnyMapping, None] = None

    if PYDANTIC_V2:
        model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)
    else:

        class Config(pydantic.BaseConfig):  # pyright: ignore[reportDeprecated]
            arbitrary_types_allowed: bool = True

    def get_max_retries(self, max_retries: int) -> int:
        if isinstance(self.max_retries, NotGiven):
            return max_retries
        return self.max_retries

    # override the `construct` method so that we can run custom transformations.
    # this is necessary as we don't want to do any actual runtime type checking
    # (which means we can't use validators) but we do want to ensure that `NotGiven`
    # values are not present
    @classmethod
    def construct(
        cls,
        _fields_set: set[str] | None = None,
        **values: Any,
    ) -> FinalRequestOptions:
        kwargs: dict[str, Any] = {
            # we unconditionally call `strip_not_given` on any value
            # as it will just ignore any non-mapping types
            key: strip_not_given(value)
            for key, value in values.items()
        }
        if PYDANTIC_V2:
            return super().model_construct(_fields_set, **kwargs)
        return cast(FinalRequestOptions, super().construct(_fields_set, **kwargs))  # pyright: ignore[reportDeprecated]

    if not TYPE_CHECKING:
        # type checkers incorrectly complain about this assignment
        model_construct = construct
