import pytest

from openai._streaming import SSEDecoder


@pytest.mark.parametrize("value", ["-1", "+1000", "١٠٠٠", "1.0", "1_000"])
def test_invalid_retry_value_is_ignored(value: str) -> None:
    decoder = SSEDecoder()
    decoder.decode("retry: 2500")
    decoder.decode(f"retry: {value}")
    decoder.decode("data: {}")

    event = decoder.decode("")
    assert event is not None
    assert event.retry == 2500


def test_ascii_retry_digits_are_accepted() -> None:
    decoder = SSEDecoder()
    decoder.decode("retry: 0010")
    decoder.decode("data: {}")

    event = decoder.decode("")
    assert event is not None
    assert event.retry == 10
