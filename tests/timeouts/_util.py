from __future__ import annotations

def assert_timeout_eq(value, expected: float) -> None:
    """Assert that a timeout-like value equals the expected seconds.

    Supports plain numeric timeouts or httpx.Timeout instances.
    """
    from httpx import Timeout

    if isinstance(value, (int, float)):
        assert float(value) == expected
    elif isinstance(value, Timeout):
        assert any(
            getattr(value, f, None) in (None, expected)
            for f in ("read", "connect", "write")
        ), f"Timeout fields do not match {expected}: {value!r}"
    else:
        raise AssertionError(f"Unexpected timeout type: {type(value)}")

