from __future__ import annotations

from openai._event_handler import EventHandlerRegistry


def test_once_registration_is_scoped_to_its_event() -> None:
    def handler(_event: object) -> None:
        pass

    registry = EventHandlerRegistry()
    registry.add("persistent", handler)
    registry.add("one-shot", handler, once=True)

    assert registry.get_handlers("persistent") == [handler]
    assert registry.get_handlers("persistent") == [handler]
    assert registry.get_handlers("one-shot") == [handler]
    assert registry.get_handlers("one-shot") == []


def test_remove_only_removes_the_first_matching_registration() -> None:
    def handler(_event: object) -> None:
        pass

    registry = EventHandlerRegistry()
    registry.add("event", handler)
    registry.add("event", handler, once=True)

    registry.remove("event", handler)

    assert registry.get_handlers("event") == [handler]
    assert registry.get_handlers("event") == []


def test_merge_preserves_each_registration_mode() -> None:
    def handler(_event: object) -> None:
        pass

    source = EventHandlerRegistry()
    target = EventHandlerRegistry()
    source.add("event", handler)
    source.add("event", handler, once=True)

    source.merge_into(target)

    assert source.has_handlers("event") is False
    assert target.get_handlers("event") == [handler, handler]
    assert target.get_handlers("event") == [handler]
