import time
import anyio
import httpx
import pytest

def test_respects_retry_after_seconds(monkeypatch):
    sleeps = []

    # Evita dormir de verdade
    monkeypatch.setattr(time, "sleep", lambda s: sleeps.append(s))

    attempts = {"n": 0}

    def handler(request: httpx.Request):
        attempts["n"] += 1
        if attempts["n"] == 1:
            # 1ª tentativa falha com 429 e Retry-After: 2
            return httpx.Response(429, headers={"Retry-After": "2"}, json={"err": "rate"})
        # 2ª tentativa sucesso
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)

    from openai import OpenAI, DefaultHttpxClient

    client = OpenAI(
        max_retries=1,
        http_client=DefaultHttpxClient(transport=transport),
    )

    client.responses.create(model="gpt-4o-mini", input="hi")

    # Deve ter "dormido" ~2s antes de retry
    assert sleeps, "expected a sleep before retry"
    assert sleeps[0] >= 2.0  # pode ser >2.0 se houver jitter adicional


@pytest.mark.asyncio
async def test_respects_retry_after_seconds_async(monkeypatch):
    sleeps = []

    async def fake_sleep(s):
        sleeps.append(s)

    monkeypatch.setattr(anyio, "sleep", fake_sleep)

    attempts = {"n": 0}

    async def handler(request: httpx.Request):
        attempts["n"] += 1
        if attempts["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "2"}, json={"err": "rate"})
        return httpx.Response(200, json={"ok": True})
        import time
        import anyio
        import httpx
        import pytest

        def test_respects_retry_after_seconds(monkeypatch):
            sleeps = []
            monkeypatch.setattr(time, "sleep", lambda s: sleeps.append(s))
            attempts = {"n": 0}

            def handler(request: httpx.Request):
                attempts["n"] += 1
                if attempts["n"] == 1:
                    return httpx.Response(429, headers={"Retry-After": "2"}, json={"err": "rate"})
                return httpx.Response(200, json={"ok": True})

            transport = httpx.MockTransport(handler)
            from openai import OpenAI, DefaultHttpxClient

            client = OpenAI(
                max_retries=1,
                http_client=DefaultHttpxClient(transport=transport),
            )

            client.responses.create(model="gpt-4o-mini", input="hi")
            assert sleeps, "expected a sleep before retry"
            assert sleeps[0] >= 2.0

        def test_no_retry_on_success(monkeypatch):
            sleeps = []
            monkeypatch.setattr(time, "sleep", lambda s: sleeps.append(s))
            attempts = {"n": 0}

            def handler(request: httpx.Request):
                attempts["n"] += 1
                return httpx.Response(200, json={"ok": True})

            transport = httpx.MockTransport(handler)
            from openai import OpenAI, DefaultHttpxClient

            client = OpenAI(
                max_retries=3,
                http_client=DefaultHttpxClient(transport=transport),
            )

            client.responses.create(model="gpt-4o-mini", input="hi")
            assert attempts["n"] == 1
            assert not sleeps

        def test_max_retries_exceeded(monkeypatch):
            sleeps = []
            monkeypatch.setattr(time, "sleep", lambda s: sleeps.append(s))
            attempts = {"n": 0}

            def handler(request: httpx.Request):
                attempts["n"] += 1
                return httpx.Response(429, headers={"Retry-After": "1"}, json={"err": "rate"})

            transport = httpx.MockTransport(handler)
            from openai import OpenAI, DefaultHttpxClient

            client = OpenAI(
                max_retries=2,
                http_client=DefaultHttpxClient(transport=transport),
            )

            with pytest.raises(httpx.HTTPStatusError):
                client.responses.create(model="gpt-4o-mini", input="hi")
            assert attempts["n"] == 3  # 1 original + 2 retries
            assert len(sleeps) == 2
            assert all(s >= 1.0 for s in sleeps)

        @pytest.mark.asyncio
        async def test_respects_retry_after_seconds_async(monkeypatch):
            sleeps = []
            async def fake_sleep(s):
                sleeps.append(s)
            monkeypatch.setattr(anyio, "sleep", fake_sleep)
            attempts = {"n": 0}

            async def handler(request: httpx.Request):
                attempts["n"] += 1
                if attempts["n"] == 1:
                    return httpx.Response(429, headers={"Retry-After": "2"}, json={"err": "rate"})
                return httpx.Response(200, json={"ok": True})

            transport = httpx.MockTransport(handler)
            from openai import AsyncOpenAI, DefaultAsyncHttpxClient

            client = AsyncOpenAI(
                max_retries=1,
                http_client=DefaultAsyncHttpxClient(transport=transport),
            )

            await client.responses.create(model="gpt-4o-mini", input="hi")
            assert sleeps
            assert sleeps[0] >= 2.0

        @pytest.mark.asyncio
        async def test_no_retry_on_success_async(monkeypatch):
            sleeps = []
            async def fake_sleep(s):
                sleeps.append(s)
            monkeypatch.setattr(anyio, "sleep", fake_sleep)
            attempts = {"n": 0}

            async def handler(request: httpx.Request):
                attempts["n"] += 1
                return httpx.Response(200, json={"ok": True})

            transport = httpx.MockTransport(handler)
            from openai import AsyncOpenAI, DefaultAsyncHttpxClient

            client = AsyncOpenAI(
                max_retries=3,
                http_client=DefaultAsyncHttpxClient(transport=transport),
            )

            await client.responses.create(model="gpt-4o-mini", input="hi")
            assert attempts["n"] == 1
            assert not sleeps

        @pytest.mark.asyncio
        async def test_max_retries_exceeded_async(monkeypatch):
            sleeps = []
            async def fake_sleep(s):
                sleeps.append(s)
            monkeypatch.setattr(anyio, "sleep", fake_sleep)
            attempts = {"n": 0}

            async def handler(request: httpx.Request):
                attempts["n"] += 1
                return httpx.Response(429, headers={"Retry-After": "1"}, json={"err": "rate"})

            transport = httpx.MockTransport(handler)
            from openai import AsyncOpenAI, DefaultAsyncHttpxClient

            client = AsyncOpenAI(
                max_retries=2,
                http_client=DefaultAsyncHttpxClient(transport=transport),
            )

            with pytest.raises(httpx.HTTPStatusError):
                await client.responses.create(model="gpt-4o-mini", input="hi")
            assert attempts["n"] == 3
            assert len(sleeps) == 2
            assert all(s >= 1.0 for s in sleeps)

        def test_retry_with_jitter(monkeypatch):
            # Testa se o retry respeita jitter (se implementado)
            sleeps = []
            monkeypatch.setattr(time, "sleep", lambda s: sleeps.append(s))
            attempts = {"n": 0}

            def handler(request: httpx.Request):
                attempts["n"] += 1
                if attempts["n"] < 3:
                    return httpx.Response(429, headers={"Retry-After": "1"}, json={"err": "rate"})
                return httpx.Response(200, json={"ok": True})

            transport = httpx.MockTransport(handler)
            from openai import OpenAI, DefaultHttpxClient

            client = OpenAI(
                max_retries=2,
                http_client=DefaultHttpxClient(transport=transport),
            )

            with pytest.raises(httpx.HTTPStatusError):
                client.responses.create(model="gpt-4o-mini", input="hi")
            assert attempts["n"] == 3
            assert len(sleeps) == 2

        def test_retry_on_different_status(monkeypatch):
            # Testa se o retry ocorre para outros status além de 429, se suportado
            sleeps = []
            monkeypatch.setattr(time, "sleep", lambda s: sleeps.append(s))
            attempts = {"n": 0}

            def handler(request: httpx.Request):
                attempts["n"] += 1
                if attempts["n"] == 1:
                    return httpx.Response(500, json={"err": "server"})
                return httpx.Response(200, json={"ok": True})

            transport = httpx.MockTransport(handler)
            from openai import OpenAI, DefaultHttpxClient

            client = OpenAI(
                max_retries=1,
                http_client=DefaultHttpxClient(transport=transport),
            )

            client.responses.create(model="gpt-4o-mini", input="hi")
            assert attempts["n"] == 2

        # Estrutura assim está ótima: cada teste cobre um cenário e está bem separado.
        # Se quiser, pode criar subpastas em tests/ para agrupar por tema (ex: tests/retries/, tests/timeouts/), mas para projetos pequenos/médios, manter arquivos separados já é suficiente e claro.
