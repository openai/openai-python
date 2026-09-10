from openai import types
from openai.types import websocket_connection_options


def test_submodule_alias_is_preserved() -> None:
    assert (
        websocket_connection_options.WebsocketConnectionOptions
        is websocket_connection_options.WebSocketConnectionOptions
    )


def test_public_types_alias_is_preserved() -> None:
    assert types.WebsocketConnectionOptions is types.WebSocketConnectionOptions


def test_beta_realtime_import_still_works_with_old_alias() -> None:
    from openai.resources.beta.realtime.realtime import Realtime, AsyncRealtime

    assert Realtime.__name__ == "Realtime"
    assert AsyncRealtime.__name__ == "AsyncRealtime"
