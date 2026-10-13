"""Run local screenshot-budget checks without a provider account."""

from __future__ import annotations

import json
import zlib
import base64
import struct
import asyncio
import inspect
import importlib.util
from io import BytesIO
from types import ModuleType, SimpleNamespace
from typing import Any, Protocol
from pathlib import Path
from contextlib import contextmanager
from collections.abc import Iterator, Awaitable, Generator

from PIL import Image

from openai.lib.computer import Screenshot

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
NORMAL = bytes.fromhex(
    "89504e470d0a1a0a0000000d494844520000000200000002080600000072b60d240000001149444154780163fc0f040c40c0c40005003df8040036184bb40000000049454e44ae426082"
)
INTERLACED = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000016812f41f0000000b49444154780163f80f040009fb03fdcf0b68720000000049454e44ae426082"
)
DEFAULT = object()


class Driver(Protocol):
    def screenshot(self) -> Screenshot | Awaitable[Screenshot]: ...


def load(vendor: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(vendor, ROOT / f"examples/computer-{vendor}/adapter.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def check_vendor(vendor: str) -> int:
    module = load(vendor)
    captures = 0
    removed = 0
    chunks_read = 0
    streams_closed = 0

    async def make(
        width: int, height: int, limit: object = DEFAULT, image: bytes = NORMAL, byte_limit: object = DEFAULT
    ) -> Driver:
        # Deliberately include invalid caller values at this example's public boundary.
        kwargs: dict[str, Any] = {} if limit is DEFAULT else {"max_screenshot_pixels": limit}
        if byte_limit is not DEFAULT:
            kwargs["max_screenshot_bytes"] = byte_limit
        if vendor == "daytona":

            async def info() -> SimpleNamespace:
                display = SimpleNamespace(id=1, is_active=True, x=0, y=0, width=width, height=height)
                return SimpleNamespace(displays=[display])

            async def screenshot() -> SimpleNamespace:
                nonlocal captures
                captures += 1
                return SimpleNamespace(screenshot=base64.b64encode(image).decode())

            return await module.DaytonaComputer.from_started_desktop(
                SimpleNamespace(
                    display=SimpleNamespace(get_info=info), screenshot=SimpleNamespace(take_full_screen=screenshot)
                ),
                **kwargs,
            )

        def capture(*_args: object, **_kwargs: object) -> None:
            nonlocal captures
            captures += 1

        def remove(*_args: object) -> None:
            nonlocal removed
            removed += 1

        @contextmanager
        def read(*_args: object, **_kwargs: object) -> Generator[Iterator[bytes], None, None]:
            nonlocal streams_closed

            def chunks() -> Iterator[bytes]:
                nonlocal chunks_read
                for part in (image[:7], image[7:20], image[20:33]):
                    chunks_read += 1
                    yield part
                for offset in range(33, len(image), 4096):
                    chunks_read += 1
                    yield image[offset : offset + 4096]

            try:
                yield chunks()
            finally:
                streams_closed += 1

        return module.E2BComputer.from_started_desktop(
            SimpleNamespace(
                sandbox_id="local-fixture",
                get_screen_size=lambda: (width, height),
                commands=SimpleNamespace(run=capture),
                files=SimpleNamespace(read=read, remove=remove),
            ),
            **kwargs,
        )

    async def shot(driver: Driver) -> Screenshot:
        result = driver.screenshot()
        return await result if inspect.isawaitable(result) else result

    async def refused(operation: Awaitable[object]) -> None:
        try:
            await operation
        except (ValueError, RuntimeError):
            return
        raise AssertionError("Expected refusal")

    await refused(make(2, 2, 3))
    assert captures == 0
    normal = await shot(await make(2, 2, 4))
    assert "image_url" in normal
    assert normal["image_url"] == "data:image/png;base64," + base64.b64encode(NORMAL).decode()
    await make(7680, 4320)
    await refused(make(7680, 4321))
    await make(7680, 4321, 7680 * 4321)
    for invalid in (0, -1, 1.5, float("nan"), float("inf"), "4", None, True):
        await refused(make(2, 2, invalid))
    before = removed
    await refused(shot(await make(1, 1, DEFAULT, INTERLACED)))
    if vendor == "e2b":
        assert removed == before + 1
        metadata = b"Comment\0" + b"x" * 300_000
        chunk = struct.pack(">I", len(metadata)) + b"tEXt" + metadata
        chunk += struct.pack(">I", zlib.crc32(chunk[4:]))
        tagged = NORMAL[:33] + chunk + NORMAL[33:]
        with Image.open(BytesIO(tagged)) as valid:
            valid.load()
            assert valid.size == (2, 2)
        prior_reads, prior_closed, prior_removed = chunks_read, streams_closed, removed
        limited = await make(2, 2, image=tagged)
        await refused(shot(limited))
        assert chunks_read - prior_reads < 3 + (len(tagged) - 33 + 4095) // 4096
        assert streams_closed == prior_closed + 1 and removed == prior_removed + 1
        after_reads = chunks_read
        await refused(shot(limited))
        assert chunks_read == after_reads
        raised = await shot(await make(2, 2, image=tagged, byte_limit=len(tagged)))
        assert "image_url" in raised
        assert raised["image_url"] == "data:image/png;base64," + base64.b64encode(tagged).decode()
        exact = await shot(await make(2, 2, byte_limit=len(NORMAL)))
        assert "image_url" in exact
        assert exact["image_url"] == "data:image/png;base64," + base64.b64encode(NORMAL).decode()
        await refused(shot(await make(2, 2, byte_limit=len(NORMAL) - 1)))
        for invalid in (0, -1, 1.5, float("nan"), float("inf"), "4", True):
            await refused(make(2, 2, byte_limit=invalid))
        # Compression level is a PNG encoding choice, not a display limit.
        with BytesIO() as encoded:
            Image.new("RGB", (2048, 1536), color="white").save(encoded, "PNG", compress_level=0)
            large = encoded.getvalue()
        assert len(large) > 8 * 1024 * 1024
        before = removed
        frame = await shot(await make(2048, 1536, DEFAULT, large))
        assert "image_url" in frame
        assert base64.b64decode(frame["image_url"].split(",", 1)[1], validate=True) == large
        assert removed == before + 1
        for malformed in (NORMAL[:32], NORMAL[:33], NORMAL[:-12], b"x" * 64):
            before = removed
            await refused(shot(await make(2, 2, DEFAULT, malformed)))
            assert removed == before + 1
        return 13
    return 7


async def main() -> None:
    with Image.open(BytesIO(INTERLACED)) as image:
        image.load()
        assert image.size == (1, 1)
    checks = await check_vendor("daytona")
    checks += await check_vendor("e2b")
    print(json.dumps({"checks": checks, "api_calls": 0, "vendor_calls": 0}))


asyncio.run(main())
