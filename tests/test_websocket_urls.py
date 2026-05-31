from __future__ import annotations

from openai import OpenAI


def test_realtime_websocket_url_preserves_http_base_url_query_param() -> None:
    client = OpenAI(
        base_url="http://example.com/v1/?next=http://example.test/callback",
        api_key="key",
    )
    manager = client.realtime.connect(model="gpt-realtime")

    prepared_url = manager._prepare_url()
    url = prepared_url.copy_with(
        params={
            **client.base_url.params,
            **prepared_url.params,
            "model": "gpt-realtime",
        }
    )

    assert str(url) == (
        "ws://example.com/v1/realtime?next=http%3A%2F%2Fexample.test%2Fcallback%2F&model=gpt-realtime"
    )


def test_realtime_websocket_url_preserves_websocket_base_url_query_param() -> None:
    client = OpenAI(
        base_url="https://example.com/v1/?base=1",
        websocket_base_url="wss://ws.example.com/socket?next=http://example.test/callback",
        api_key="key",
    )
    manager = client.realtime.connect(model="gpt-realtime")

    prepared_url = manager._prepare_url()
    url = prepared_url.copy_with(
        params={
            **client.base_url.params,
            **prepared_url.params,
            "model": "gpt-realtime",
        }
    )

    assert str(url) == (
        "wss://ws.example.com/socket/realtime?base=1%2F&next=http%3A%2F%2Fexample.test%2Fcallback&model=gpt-realtime"
    )


def test_responses_websocket_url_preserves_base_url_query_param() -> None:
    client = OpenAI(
        base_url="https://example.com/v1/?next=http://example.test/callback",
        api_key="key",
    )
    manager = client.responses.connect(extra_query={"foo": "bar"})

    prepared_url = manager._prepare_url()
    url = prepared_url.copy_with(
        params={
            **client.base_url.params,
            **prepared_url.params,
            "foo": "bar",
        }
    )

    assert str(url) == "wss://example.com/v1/responses?next=http%3A%2F%2Fexample.test%2Fcallback%2F&foo=bar"


def test_beta_realtime_websocket_url_preserves_base_url_query_param() -> None:
    client = OpenAI(
        base_url="https://example.com/v1/?next=http://example.test/callback",
        api_key="key",
    )
    manager = client.beta.realtime.connect(model="gpt-realtime")

    prepared_url = manager._prepare_url()
    url = prepared_url.copy_with(
        params={
            **client.base_url.params,
            **prepared_url.params,
            "model": "gpt-realtime",
        }
    )

    assert str(url) == (
        "wss://example.com/v1/realtime?next=http%3A%2F%2Fexample.test%2Fcallback%2F&model=gpt-realtime"
    )
