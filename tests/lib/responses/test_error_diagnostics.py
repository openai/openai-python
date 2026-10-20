from __future__ import annotations

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI


@pytest.mark.parametrize("route", ["responses", "beta", "videos"])
@pytest.mark.parametrize("sync", [False, True])
@pytest.mark.parametrize("shape", ["values", "nulls", "omitted"])
async def test_error_diagnostics_transport(route: str, sync: bool, shape: str) -> None:
    error: dict[str, object] = {"code": "server_error", "message": "Synthetic failure"}
    if shape != "omitted":
        error.update(
            type="synthetic_error" if shape == "values" else None, param="input[0]" if shape == "values" else None
        )
    video = route == "videos"
    identifier = "video_synthetic" if video else "resp_synthetic"
    requests: list[httpx2.Request] = []

    def respond(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        assert request.method == "GET"
        assert request.url.path == f"/{'videos' if video else 'responses'}/{identifier}"
        assert request.url.params.get("beta") == ("true" if route == "beta" else None)
        return httpx2.Response(200, json={"id": identifier, "error": error})

    transport = httpx2.MockTransport(respond)
    if sync:
        with OpenAI(
            api_key="fake-test-key", base_url="https://example.test", http_client=httpx2.Client(transport=transport)
        ) as client:
            if video:
                # Exercise the retained deprecated API and verify its runtime warning.
                with pytest.warns(DeprecationWarning, match="Sora API"):
                    result = client.videos.retrieve(identifier)  # pyright: ignore[reportDeprecated]
            else:
                result = (client.beta.responses if route == "beta" else client.responses).retrieve(identifier)
    else:
        async with AsyncOpenAI(
            api_key="fake-test-key",
            base_url="https://example.test",
            http_client=httpx2.AsyncClient(transport=transport),
        ) as client_async:
            if video:
                # Exercise the retained deprecated API and verify its runtime warning.
                with pytest.warns(DeprecationWarning, match="Sora API"):
                    result = await client_async.videos.retrieve(identifier)  # pyright: ignore[reportDeprecated]
            else:
                result = await (client_async.beta.responses if route == "beta" else client_async.responses).retrieve(
                    identifier
                )
    assert len(requests) == 1
    assert result.error is not None
    assert result.error.type == ("synthetic_error" if shape == "values" else None)
    assert result.error.param == ("input[0]" if shape == "values" else None)
    assert result.error.code == "server_error"
    assert result.error.message == "Synthetic failure"
