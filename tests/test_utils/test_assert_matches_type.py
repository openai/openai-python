import json
from http import HTTPStatus
from typing import Any, Literal, Iterator, Sequence
from threading import Thread
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import SplitResult, parse_qs, urlsplit
from typing_extensions import override

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types import Model
from openai.pagination import SyncPage, AsyncPage


@pytest.mark.parametrize(
    ("type_", "value"),
    [
        (list[int], [1, "wrong"]),
        (Sequence[int], (1, "wrong")),
        (list[list[int]], [[1], ["wrong"]]),
        (Sequence[list[int]], ([1], ["wrong"])),
        (list[dict[str, int]], [{"value": "wrong"}]),
        (dict[str, list[int]], {"values": ["wrong"]}),
        (list[Literal["expected"]], ["wrong"]),
    ],
)
def test_rejects_invalid_sequence_members(type_: Any, value: object) -> None:
    with pytest.raises(AssertionError):
        assert_matches_type(type_=type_, value=value, path=["response"])


@pytest.mark.parametrize(
    ("type_", "value"),
    [
        (list[int], [1, 2]),
        (Sequence[int], (1, 2)),
        (list[list[int]], [[1], []]),
        (Sequence[list[int]], ([1], [2])),
        (list[dict[str, int]], [{"value": 1}]),
        (list[Any], [1, "value", None]),
        (Sequence[Any], (1, "value", None)),
    ],
)
def test_accepts_valid_sequence_members(type_: Any, value: object) -> None:
    assert_matches_type(type_=type_, value=value, path=["response"])


@pytest.fixture
def models_api_url() -> Iterator[str]:
    class ModelsHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            request: SplitResult = urlsplit(self.path)
            if request.path != "/v1/models":
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            invalid: bool = parse_qs(request.query).get("case") == ["invalid"]
            body: bytes = json.dumps(
                {
                    "object": "list",
                    "data": [
                        {
                            "id": "test-model",
                            "created": "not-an-integer" if invalid else 0,
                            "object": "model",
                            "owned_by": "test",
                        }
                    ],
                }
            ).encode()
            self.send_response(HTTPStatus.OK)
            self.send_header(keyword="Content-Type", value="application/json")
            self.send_header(keyword="Content-Length", value=str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        @override
        def log_message(self, format: str, *_args: object) -> None:  # noqa: A002
            return None

    server = ThreadingHTTPServer(server_address=("127.0.0.1", 0), RequestHandlerClass=ModelsHandler)
    thread = Thread(target=server.serve_forever)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/v1"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def check_response(*, mode: str, response: SyncPage[Model] | AsyncPage[Model], invalid: bool) -> None:
    try:
        assert_matches_type(type_=type(response), value=response, path=["response"])
    except AssertionError:
        rejected = True
    else:
        rejected = False
    print(
        f"{mode} invalid={invalid} created_type={type(response.data[0].created).__name__} rejected={rejected}",
        flush=True,
    )
    assert rejected == invalid


@pytest.mark.parametrize("invalid", [False, True])
def test_models_api_types(models_api_url: str, invalid: bool) -> None:
    with OpenAI(
        api_key="local-test-key",
        admin_api_key="local-test-admin-key",
        organization="test-org",
        project="test-project",
        base_url=models_api_url,
        http_client=httpx2.Client(trust_env=False),
    ) as client:
        response: SyncPage[Model] = client.models.list(extra_query={"case": "invalid" if invalid else "valid"})
    check_response(mode="sync", response=response, invalid=invalid)


@pytest.mark.parametrize("invalid", [False, True])
async def test_async_models_api_types(models_api_url: str, invalid: bool) -> None:
    async with AsyncOpenAI(
        api_key="local-test-key",
        admin_api_key="local-test-admin-key",
        organization="test-org",
        project="test-project",
        base_url=models_api_url,
        http_client=httpx2.AsyncClient(trust_env=False),
    ) as client:
        response: AsyncPage[Model] = await client.models.list(extra_query={"case": "invalid" if invalid else "valid"})
    check_response(mode="async", response=response, invalid=invalid)
