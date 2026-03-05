"""
Copied from https://github.com/pydantic/pydantic/blob/v1.10.22/tests/test_datetime_parse.py
with modifications so it works without pydantic v1 imports.
"""

from typing import Type, Union
from datetime import date, datetime, timezone, timedelta

import pytest

from openai._utils import parse_date, parse_datetime


def create_tz(minutes: int) -> timezone:
    return timezone(timedelta(minutes=minutes))


@pytest.mark.parametrize(
    "value,result",
    [
        # Valid inputs
        ("1494012444.883309", date(2017, 5, 5)),
        (b"1494012444.883309", date(2017, 5, 5)),
        (1_494_012_444.883_309, date(2017, 5, 5)),
        ("1494012444", date(2017, 5, 5)),
        (1_494_012_444, date(2017, 5, 5)),
        (0, date(1970, 1, 1)),
        ("2012-04-23", date(2012, 4, 23)),
        (b"2012-04-23", date(2012, 4, 23)),
        ("2012-4-9", date(2012, 4, 9)),
        (date(2012, 4, 9), date(2012, 4, 9)),
        (datetime(2012, 4, 9, 12, 15), date(2012, 4, 9)),
        # Invalid inputs
        ("x20120423", ValueError),
        ("2012-04-56", ValueError),
        (19_999_999_999, date(2603, 10, 11)),  # just before watershed
        (20_000_000_001, date(1970, 8, 20)),  # just after watershed
        (1_549_316_052, date(2019, 2, 4)),  # nowish in s
        (1_549_316_052_104, date(2019, 2, 4)),  # nowish in ms
        (1_549_316_052_104_324, date(2019, 2, 4)),  # nowish in μs
        (1_549_316_052_104_324_096, date(2019, 2, 4)),  # nowish in ns
        ("infinity", date(9999, 12, 31)),
        ("inf", date(9999, 12, 31)),
        (float("inf"), date(9999, 12, 31)),
        ("infinity ", date(9999, 12, 31)),
        (int("1" + "0" * 100), date(9999, 12, 31)),
        (1e1000, date(9999, 12, 31)),
        ("-infinity", date(1, 1, 1)),
        ("-inf", date(1, 1, 1)),
        ("nan", ValueError),
    ],
)
def test_date_parsing(value: Union[str, bytes, int, float], result: Union[date, Type[Exception]]) -> None:
    if type(result) == type and issubclass(result, Exception):  # pyright: ignore[reportUnnecessaryIsInstance]
        with pytest.raises(result):
            parse_date(value)
    else:
        assert parse_date(value) == result


@pytest.mark.parametrize(
    "value,result",
    [
        # Valid inputs
        # values in seconds
        ("1494012444.883309", datetime(2017, 5, 5, 19, 27, 24, 883_309, tzinfo=timezone.utc)),
        (1_494_012_444.883_309, datetime(2017, 5, 5, 19, 27, 24, 883_309, tzinfo=timezone.utc)),
        ("1494012444", datetime(2017, 5, 5, 19, 27, 24, tzinfo=timezone.utc)),
        (b"1494012444", datetime(2017, 5, 5, 19, 27, 24, tzinfo=timezone.utc)),
        (1_494_012_444, datetime(2017, 5, 5, 19, 27, 24, tzinfo=timezone.utc)),
        # values in ms
        ("1494012444000.883309", datetime(2017, 5, 5, 19, 27, 24, 883, tzinfo=timezone.utc)),
        ("-1494012444000.883309", datetime(1922, 8, 29, 4, 32, 35, 999117, tzinfo=timezone.utc)),
        (1_494_012_444_000, datetime(2017, 5, 5, 19, 27, 24, tzinfo=timezone.utc)),
        ("2012-04-23T09:15:00", datetime(2012, 4, 23, 9, 15)),
        ("2012-4-9 4:8:16", datetime(2012, 4, 9, 4, 8, 16)),
        ("2012-04-23T09:15:00Z", datetime(2012, 4, 23, 9, 15, 0, 0, timezone.utc)),
        ("2012-4-9 4:8:16-0320", datetime(2012, 4, 9, 4, 8, 16, 0, create_tz(-200))),
        ("2012-04-23T10:20:30.400+02:30", datetime(2012, 4, 23, 10, 20, 30, 400_000, create_tz(150))),
        ("2012-04-23T10:20:30.400+02", datetime(2012, 4, 23, 10, 20, 30, 400_000, create_tz(120))),
        ("2012-04-23T10:20:30.400-02", datetime(2012, 4, 23, 10, 20, 30, 400_000, create_tz(-120))),
        (b"2012-04-23T10:20:30.400-02", datetime(2012, 4, 23, 10, 20, 30, 400_000, create_tz(-120))),
        (datetime(2017, 5, 5), datetime(2017, 5, 5)),
        (0, datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)),
        # Invalid inputs
        ("x20120423091500", ValueError),
        ("2012-04-56T09:15:90", ValueError),
        ("2012-04-23T11:05:00-25:00", ValueError),
        (19_999_999_999, datetime(2603, 10, 11, 11, 33, 19, tzinfo=timezone.utc)),  # just before watershed
        (20_000_000_001, datetime(1970, 8, 20, 11, 33, 20, 1000, tzinfo=timezone.utc)),  # just after watershed
        (1_549_316_052, datetime(2019, 2, 4, 21, 34, 12, 0, tzinfo=timezone.utc)),  # nowish in s
        (1_549_316_052_104, datetime(2019, 2, 4, 21, 34, 12, 104_000, tzinfo=timezone.utc)),  # nowish in ms
        (1_549_316_052_104_324, datetime(2019, 2, 4, 21, 34, 12, 104_324, tzinfo=timezone.utc)),  # nowish in μs
        (1_549_316_052_104_324_096, datetime(2019, 2, 4, 21, 34, 12, 104_324, tzinfo=timezone.utc)),  # nowish in ns
        ("infinity", datetime(9999, 12, 31, 23, 59, 59, 999999)),
        ("inf", datetime(9999, 12, 31, 23, 59, 59, 999999)),
        ("inf ", datetime(9999, 12, 31, 23, 59, 59, 999999)),
        (1e50, datetime(9999, 12, 31, 23, 59, 59, 999999)),
        (float("inf"), datetime(9999, 12, 31, 23, 59, 59, 999999)),
        ("-infinity", datetime(1, 1, 1, 0, 0)),
        ("-inf", datetime(1, 1, 1, 0, 0)),
        ("nan", ValueError),
    ],
)
def test_datetime_parsing(value: Union[str, bytes, int, float], result: Union[datetime, Type[Exception]]) -> None:
    if type(result) == type and issubclass(result, Exception):  # pyright: ignore[reportUnnecessaryIsInstance]
        with pytest.raises(result):
            parse_datetime(value)
    else:
        assert parse_datetime(value) == result
