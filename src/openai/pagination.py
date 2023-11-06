# File generated from our OpenAPI spec by Stainless.

from typing import Any, List, Generic, TypeVar, Optional, cast
from typing_extensions import Literal, Protocol, override, runtime_checkable

from ._types import ModelT
from ._models import BaseModel
from ._base_client import BasePage, PageInfo, BaseSyncPage, BaseAsyncPage

__all__ = ["SyncPage", "AsyncPage", "SyncCursorPage", "AsyncCursorPage"]

_BaseModelT = TypeVar("_BaseModelT", bound=BaseModel)


@runtime_checkable
class CursorPageItem(Protocol):
    id: str


class SyncPage(BaseSyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    """Note: no pagination actually occurs yet, this is for forwards-compatibility."""

    data: List[ModelT]
    object: Literal["list"]

    @override
    def _get_page_items(self) -> List[ModelT]:
        return self.data

    @override
    def next_page_info(self) -> None:
        """
        This page represents a response that isn't actually paginated at the API level
        so there will never be a next page.
        """
        return None


class AsyncPage(BaseAsyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    """Note: no pagination actually occurs yet, this is for forwards-compatibility."""

    data: List[ModelT]
    object: Literal["list"]

    @override
    def _get_page_items(self) -> List[ModelT]:
        return self.data

    @override
    def next_page_info(self) -> None:
        """
        This page represents a response that isn't actually paginated at the API level
        so there will never be a next page.
        """
        return None


class SyncCursorPage(BaseSyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    data: List[ModelT]

    @override
    def _get_page_items(self) -> List[ModelT]:
        return self.data

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        if not self.data:
            return None

        item = cast(Any, self.data[-1])
        if not isinstance(item, CursorPageItem):
            # TODO emit warning log
            return None

        return PageInfo(params={"after": item.id})


class AsyncCursorPage(BaseAsyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    data: List[ModelT]

    @override
    def _get_page_items(self) -> List[ModelT]:
        return self.data

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        if not self.data:
            return None

        item = cast(Any, self.data[-1])
        if not isinstance(item, CursorPageItem):
            # TODO emit warning log
            return None

        return PageInfo(params={"after": item.id})
