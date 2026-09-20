"""Envelope-cursor pages must agree between `has_next_page()` and `next_page_info()`.

`SyncCursorPage` derives its cursor from the last item in `data`, so an empty page
genuinely has no next page. The other page classes take the cursor from the response
envelope (`last_id` / `next`), which `next_page_info()` reads without looking at
`data`. For those classes `BasePage.has_next_page()`'s empty-`data` short-circuit
contradicts `next_page_info()` and `get_next_page()`, and `iter_pages()` /
`auto_paging_iter()` stop early on a page the server explicitly said continues.
"""

from typing import Any, List

import pytest

from openai.pagination import (
    SyncTokenPage,
    AsyncTokenPage,
    SyncCursorPage,
    SyncNextCursorPage,
    AsyncNextCursorPage,
    SyncConversationCursorPage,
    AsyncConversationCursorPage,
)

ENVELOPE_CURSOR_PAGES: List[Any] = [
    SyncConversationCursorPage,
    AsyncConversationCursorPage,
    SyncNextCursorPage,
    AsyncNextCursorPage,
    SyncTokenPage,
    AsyncTokenPage,
]


def _cursor_field(page_cls: Any) -> str:
    return "last_id" if "Conversation" in page_cls.__name__ else "next"


@pytest.mark.parametrize("page_cls", ENVELOPE_CURSOR_PAGES, ids=lambda c: c.__name__)
def test_empty_page_with_envelope_cursor_still_has_next_page(page_cls: Any) -> None:
    """Regression: `has_next_page()` returned False while `next_page_info()` returned a
    usable cursor, so auto-paging silently dropped every remaining page."""
    page = page_cls(data=[], has_more=True, **{_cursor_field(page_cls): "cursor_1"})

    info = page.next_page_info()
    assert info is not None
    assert page.has_next_page() is True, "has_next_page() contradicts next_page_info(): the envelope cursor is usable"


@pytest.mark.parametrize("page_cls", ENVELOPE_CURSOR_PAGES, ids=lambda c: c.__name__)
def test_non_empty_page_behaviour_unchanged(page_cls: Any) -> None:
    page = page_cls(data=[{"id": "obj_1"}], has_more=True, **{_cursor_field(page_cls): "cursor_1"})
    assert page.has_next_page() is True


@pytest.mark.parametrize("page_cls", ENVELOPE_CURSOR_PAGES, ids=lambda c: c.__name__)
def test_has_more_false_still_wins(page_cls: Any) -> None:
    """`has_more: false` must short-circuit even when a cursor is echoed back."""
    page = page_cls(data=[], has_more=False, **{_cursor_field(page_cls): "cursor_1"})
    assert page.has_next_page() is False


@pytest.mark.parametrize("page_cls", ENVELOPE_CURSOR_PAGES, ids=lambda c: c.__name__)
def test_empty_page_without_cursor_has_no_next_page(page_cls: Any) -> None:
    page: Any = page_cls(data=[], has_more=True, **{_cursor_field(page_cls): None})
    assert page.next_page_info() is None
    assert page.has_next_page() is False


def test_item_cursor_page_keeps_empty_data_short_circuit() -> None:
    """`SyncCursorPage` takes its cursor from `data[-1].id`, so an empty page has no
    next page; that class must keep returning False."""
    page: SyncCursorPage[Any] = SyncCursorPage(data=[], has_more=True)
    assert page.next_page_info() is None
    assert page.has_next_page() is False


def test_iter_pages_stops_only_when_the_cursor_is_exhausted() -> None:
    """The public paging contract, without a client: the page must advertise the
    next page exactly when `next_page_info()` can build the request for it."""
    page: Any = SyncNextCursorPage(data=[], has_more=True, next="cursor_1")
    assert page.has_next_page() is (page.next_page_info() is not None)
    assert page.has_next_page() is True
