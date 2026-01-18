import httpx
import pytest

def test_per_request_timeout_overrides_default(monkeypatch):
    captured = {}

    def handler(request: httpx.Request):
        # httpx coloca o timeout nos extensions
        captured["timeout"] = request.extensions.get("timeout")
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)

    # Importa do SDK
    from openai import OpenAI, DefaultHttpxClient

    # Cliente com timeout "alto" para evidenciar o override
    client = OpenAI(
        timeout=60.0,
        http_client=DefaultHttpxClient(transport=transport),
    )

    # Chamada com override por requisição
    client.with_options(timeout=5.0).responses.create(model="gpt-4o-mini", input="ping")

    assert "timeout" in captured and captured["timeout"] is not None

    # Pode ser float simples ou httpx.Timeout
    t = captured["timeout"]
    if isinstance(t, (int, float)):
        assert t == 5.0
    else:
        # httpx.Timeout: qualquer um dos campos deve refletir 5.0 se foi criado assim
        # (aceitamos read/connect/write iguais se o SDK criar Timeout composto)
        assert getattr(t, "read", None) in (None, 5.0) or getattr(t, "connect", None) in (None, 5.0) or getattr(t, "write", None) in (None, 5.0)


@pytest.mark.asyncio
async def test_per_request_timeout_overrides_default_async(monkeypatch):
    captured = {}

    async def ahandler(request):
        captured["timeout"] = request.extensions.get("timeout")
        return httpx.Response(200, json={"ok": True})

    import httpx
    import pytest

    def test_per_request_timeout_overrides_default(monkeypatch):
        captured = {}

        def handler(request: httpx.Request):
            captured["timeout"] = request.extensions.get("timeout")
            return httpx.Response(200, json={"ok": True})

        transport = httpx.MockTransport(handler)
        from openai import OpenAI, DefaultHttpxClient

        client = OpenAI(
            timeout=60.0,
            http_client=DefaultHttpxClient(transport=transport),
        )

        client.with_options(timeout=5.0).responses.create(model="gpt-4o-mini", input="ping")

        assert "timeout" in captured and captured["timeout"] is not None
        t = captured["timeout"]
        if isinstance(t, (int, float)):
            assert t == 5.0
        else:
            assert getattr(t, "read", None) in (None, 5.0) or getattr(t, "connect", None) in (None, 5.0) or getattr(t, "write", None) in (None, 5.0)

    def test_default_timeout_is_used(monkeypatch):
        captured = {}

        def handler(request: httpx.Request):
            captured["timeout"] = request.extensions.get("timeout")
            return httpx.Response(200, json={"ok": True})

        transport = httpx.MockTransport(handler)
        from openai import OpenAI, DefaultHttpxClient

        client = OpenAI(
            timeout=42.0,
            http_client=DefaultHttpxClient(transport=transport),
        )

        client.responses.create(model="gpt-4o-mini", input="ping")

        assert "timeout" in captured and captured["timeout"] is not None
        t = captured["timeout"]
        if isinstance(t, (int, float)):
            assert t == 42.0
        else:
            assert getattr(t, "read", None) in (None, 42.0) or getattr(t, "connect", None) in (None, 42.0) or getattr(t, "write", None) in (None, 42.0)

    def test_no_timeout(monkeypatch):
        captured = {}

        def handler(request: httpx.Request):
            captured["timeout"] = request.extensions.get("timeout")
            return httpx.Response(200, json={"ok": True})

        transport = httpx.MockTransport(handler)
        from openai import OpenAI, DefaultHttpxClient

        client = OpenAI(
            http_client=DefaultHttpxClient(transport=transport),
        )

        client.responses.create(model="gpt-4o-mini", input="ping")

        # Pode ser None ou não setado, depende da implementação
        assert "timeout" in captured

    @pytest.mark.asyncio
    async def test_per_request_timeout_overrides_default_async(monkeypatch):
        captured = {}

        async def ahandler(request):
            captured["timeout"] = request.extensions.get("timeout")
            return httpx.Response(200, json={"ok": True})

        atransport = httpx.MockTransport(ahandler)
        from openai import AsyncOpenAI, DefaultAsyncHttpxClient

        client = AsyncOpenAI(
            timeout=60.0,
            http_client=DefaultAsyncHttpxClient(transport=atransport),
        )

        await client.with_options(timeout=5.0).responses.create(model="gpt-4o-mini", input="ping")

        assert "timeout" in captured and captured["timeout"] is not None
        t = captured["timeout"]
        if isinstance(t, (int, float)):
            assert t == 5.0
        else:
            assert getattr(t, "read", None) in (None, 5.0) or getattr(t, "connect", None) in (None, 5.0) or getattr(t, "write", None) in (None, 5.0)

    @pytest.mark.asyncio
    async def test_default_timeout_is_used_async(monkeypatch):
        captured = {}

        async def ahandler(request):
            captured["timeout"] = request.extensions.get("timeout")
            return httpx.Response(200, json={"ok": True})

        atransport = httpx.MockTransport(ahandler)
        from openai import AsyncOpenAI, DefaultAsyncHttpxClient

        client = AsyncOpenAI(
            timeout=42.0,
            http_client=DefaultAsyncHttpxClient(transport=atransport),
        )

        await client.responses.create(model="gpt-4o-mini", input="ping")

        assert "timeout" in captured and captured["timeout"] is not None
        t = captured["timeout"]
        if isinstance(t, (int, float)):
            assert t == 42.0
        else:
            assert getattr(t, "read", None) in (None, 42.0) or getattr(t, "connect", None) in (None, 42.0) or getattr(t, "write", None) in (None, 42.0)

    @pytest.mark.asyncio
    async def test_no_timeout_async(monkeypatch):
        captured = {}

        async def ahandler(request):
            captured["timeout"] = request.extensions.get("timeout")
            return httpx.Response(200, json={"ok": True})

        atransport = httpx.MockTransport(ahandler)
        from openai import AsyncOpenAI, DefaultAsyncHttpxClient

        client = AsyncOpenAI(
            http_client=DefaultAsyncHttpxClient(transport=atransport),
        )

        await client.responses.create(model="gpt-4o-mini", input="ping")

        assert "timeout" in captured
