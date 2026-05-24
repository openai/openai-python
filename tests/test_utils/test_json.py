from __future__ import annotations

import datetime
from typing import Union

import pydantic

from openai import _compat
from openai._utils._json import openapi_dumps


class TestOpenapiDumps:
    def test_basic(self) -> None:
        data = {"key": "value", "number": 42}
        json_bytes = openapi_dumps(data)
        assert json_bytes == b'{"key":"value","number":42}'

    def test_datetime_serialization(self) -> None:
        dt = datetime.datetime(2023, 1, 1, 12, 0, 0)
        data = {"datetime": dt}
        json_bytes = openapi_dumps(data)
        assert json_bytes == b'{"datetime":"2023-01-01T12:00:00"}'

    def test_pydantic_model_serialization(self) -> None:
        class User(pydantic.BaseModel):
            first_name: str
            last_name: str
            age: int

        model_instance = User(first_name="John", last_name="Kramer", age=83)
        data = {"model": model_instance}
        json_bytes = openapi_dumps(data)
        assert json_bytes == b'{"model":{"first_name":"John","last_name":"Kramer","age":83}}'

    def test_pydantic_model_with_default_values(self) -> None:
        class User(pydantic.BaseModel):
            name: str
            role: str = "user"
            active: bool = True
            score: int = 0

        model_instance = User(name="Alice")
        data = {"model": model_instance}
        json_bytes = openapi_dumps(data)
        assert json_bytes == b'{"model":{"name":"Alice"}}'

    def test_pydantic_model_with_default_values_overridden(self) -> None:
        class User(pydantic.BaseModel):
            name: str
            role: str = "user"
            active: bool = True

        model_instance = User(name="Bob", role="admin", active=False)
        data = {"model": model_instance}
        json_bytes = openapi_dumps(data)
        assert json_bytes == b'{"model":{"name":"Bob","role":"admin","active":false}}'

    def test_pydantic_model_with_alias(self) -> None:
        class User(pydantic.BaseModel):
            first_name: str = pydantic.Field(alias="firstName")
            last_name: str = pydantic.Field(alias="lastName")

        model_instance = User(firstName="John", lastName="Doe")
        data = {"model": model_instance}
        json_bytes = openapi_dumps(data)
        assert json_bytes == b'{"model":{"firstName":"John","lastName":"Doe"}}'

    def test_pydantic_model_with_alias_and_default(self) -> None:
        class User(pydantic.BaseModel):
            user_name: str = pydantic.Field(alias="userName")
            user_role: str = pydantic.Field(default="member", alias="userRole")
            is_active: bool = pydantic.Field(default=True, alias="isActive")

        model_instance = User(userName="charlie")
        data = {"model": model_instance}
        json_bytes = openapi_dumps(data)
        assert json_bytes == b'{"model":{"userName":"charlie"}}'

        model_with_overrides = User(userName="diana", userRole="admin", isActive=False)
        data = {"model": model_with_overrides}
        json_bytes = openapi_dumps(data)
        assert json_bytes == b'{"model":{"userName":"diana","userRole":"admin","isActive":false}}'

    def test_pydantic_model_with_nested_models_and_defaults(self) -> None:
        class Address(pydantic.BaseModel):
            street: str
            city: str = "Unknown"

        class User(pydantic.BaseModel):
            name: str
            address: Address
            verified: bool = False

        if _compat.PYDANTIC_V1:
            # to handle forward references in Pydantic v1
            User.update_forward_refs(**locals())  # type: ignore[reportDeprecated]

        address = Address(street="123 Main St")
        user = User(name="Diana", address=address)
        data = {"user": user}
        json_bytes = openapi_dumps(data)
        assert json_bytes == b'{"user":{"name":"Diana","address":{"street":"123 Main St"}}}'

        address_with_city = Address(street="456 Oak Ave", city="Boston")
        user_verified = User(name="Eve", address=address_with_city, verified=True)
        data = {"user": user_verified}
        json_bytes = openapi_dumps(data)
        assert (
            json_bytes == b'{"user":{"name":"Eve","address":{"street":"456 Oak Ave","city":"Boston"},"verified":true}}'
        )

    def test_pydantic_model_with_optional_fields(self) -> None:
        class User(pydantic.BaseModel):
            name: str
            email: Union[str, None]
            phone: Union[str, None]

        model_with_none = User(name="Eve", email=None, phone=None)
        data = {"model": model_with_none}
        json_bytes = openapi_dumps(data)
        assert json_bytes == b'{"model":{"name":"Eve","email":null,"phone":null}}'

        model_with_values = User(name="Frank", email="frank@example.com", phone=None)
        data = {"model": model_with_values}
        json_bytes = openapi_dumps(data)
        assert json_bytes == b'{"model":{"name":"Frank","email":"frank@example.com","phone":null}}'
