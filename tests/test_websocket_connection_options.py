# An invalid native-sync literal becoming accepted must fail the type check.
# pyright: reportUnnecessaryTypeIgnoreComment=true
from typing import TYPE_CHECKING

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


if TYPE_CHECKING:
    from openai import OpenAI, AsyncOpenAI
    from openai.lib.realtime_translation import TranslationSession, AsyncTranslationSession
    from openai.types.websocket_connection_options import SyncWebSocketConnectionOptions

    def native_options_contract(
        client: AsyncOpenAI,
    ) -> tuple[SyncWebSocketConnectionOptions, SyncWebSocketConnectionOptions]:
        # All synchronous native options remain representable. max_queue requires
        # websockets >=14 for a synchronous native connection.
        valid_sync: SyncWebSocketConnectionOptions = {
            "extensions": None,
            "subprotocols": None,
            "compression": None,
            "max_size": None,
            "max_queue": (8, 2),
        }
        invalid_sync: SyncWebSocketConnectionOptions = {"write_limit": 65536}  # pyright: ignore[reportAssignmentType]

        # The existing names still support async write limits on all supported
        # websocket versions, including through the generated public entrypoint.
        original: types.WebSocketConnectionOptions = {"write_limit": 65536, "max_queue": 8}
        legacy: types.WebsocketConnectionOptions = {"write_limit": (65536, 16384)}
        client.realtime.connect(model="test", websocket_connection_options=original)
        client.responses.connect(websocket_connection_options=legacy)
        return valid_sync, invalid_sync

    def beta_realtime_options_contract(client: OpenAI, async_client: AsyncOpenAI) -> None:
        client.beta.realtime.connect(model="test", websocket_connection_options={"max_size": 512})
        client.beta.realtime.connect(model="test", websocket_connection_options={"write_limit": 65536})  # pyright: ignore[reportArgumentType]
        async_client.beta.realtime.connect(model="test", websocket_connection_options={"write_limit": 65536})

    def translation_options_contract(
        client: OpenAI, async_client: AsyncOpenAI
    ) -> tuple[TranslationSession, TranslationSession, AsyncTranslationSession]:
        valid_sync = TranslationSession(
            client.realtime.translations, model="test", websocket_connection_options={"max_size": None, "max_queue": 8}
        )
        invalid_sync = TranslationSession(
            client.realtime.translations,
            model="test",
            websocket_connection_options={"write_limit": 65536},  # pyright: ignore[reportArgumentType]
        )
        valid_async = AsyncTranslationSession(
            async_client.realtime.translations, model="test", websocket_connection_options={"write_limit": 65536}
        )
        return valid_sync, invalid_sync, valid_async

    def synchronous_options_contract(client: OpenAI) -> None:
        # Native sync websockets accepts max_queue on version 14 and above.
        client.realtime.connect(model="test", websocket_connection_options={"max_queue": 8})
        client.responses.connect(websocket_connection_options={"max_size": None, "compression": None})
        client.live.connect(websocket_connection_options={"extensions": None, "subprotocols": None})

        # Native sync clients do not implement write_limit on any supported version.
        client.realtime.connect(model="test", websocket_connection_options={"write_limit": 65536})  # pyright: ignore[reportArgumentType]
        client.responses.connect(websocket_connection_options={"write_limit": 65536})  # pyright: ignore[reportArgumentType]
        client.beta.responses.connect(websocket_connection_options={"write_limit": 65536})  # pyright: ignore[reportArgumentType]
        client.live.connect(websocket_connection_options={"write_limit": 65536})  # pyright: ignore[reportArgumentType]
        client.live.sideband.connect(session_id="live_1", websocket_connection_options={"write_limit": 65536})  # pyright: ignore[reportArgumentType]
        client.live.forks.connect(session_id="live_1", websocket_connection_options={"write_limit": 65536})  # pyright: ignore[reportArgumentType]
        client.realtime.translations.connect("test", websocket_connection_options={"write_limit": 65536})  # pyright: ignore[reportArgumentType]

    def asynchronous_options_contract(client: AsyncOpenAI) -> None:
        original: types.WebSocketConnectionOptions = {"write_limit": 65536, "max_queue": 8}
        legacy: types.WebsocketConnectionOptions = {"write_limit": (65536, 16384)}
        client.realtime.connect(model="test", websocket_connection_options=original)
        client.responses.connect(websocket_connection_options=legacy)
        client.beta.responses.connect(websocket_connection_options={"write_limit": 65536})
        client.live.connect(websocket_connection_options={"write_limit": 65536})
        client.live.sideband.connect(session_id="live_1", websocket_connection_options={"write_limit": 65536})
        client.live.forks.connect(session_id="live_1", websocket_connection_options={"write_limit": 65536})
        client.realtime.translations.connect("test", websocket_connection_options={"write_limit": 65536})
