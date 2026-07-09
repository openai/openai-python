from openai.lib.streaming._deltas import accumulate_delta


def test_accumulate_delta_merges_duplicate_indexes_in_initial_list() -> None:
    acc: dict[object, object] = {"tool_calls": None}

    accumulate_delta(
        acc,
        {
            "tool_calls": [
                {
                    "index": 0,
                    "id": "call_abc",
                    "function": {"name": "get_weather"},
                    "type": "function",
                },
                {
                    "index": 0,
                    "function": {"arguments": '{"city"'},
                },
            ],
        },
    )
    accumulate_delta(
        acc,
        {
            "tool_calls": [
                {
                    "index": 0,
                    "function": {"arguments": ': "London"}'},
                },
            ],
        },
    )

    assert acc["tool_calls"] == [
        {
            "index": 0,
            "id": "call_abc",
            "function": {"name": "get_weather", "arguments": '{"city": "London"}'},
            "type": "function",
        }
    ]


def test_accumulate_delta_merges_later_entries_by_logical_index() -> None:
    acc: dict[object, object] = {
        "tool_calls": [
            {
                "index": 0,
                "function": {"arguments": "a"},
            },
            {
                "index": 1,
                "function": {"arguments": "x"},
            },
        ],
    }

    accumulate_delta(
        acc,
        {
            "tool_calls": [
                {
                    "index": 1,
                    "function": {"arguments": "y"},
                },
                {
                    "index": 0,
                    "function": {"arguments": "b"},
                },
            ],
        },
    )

    assert acc["tool_calls"] == [
        {
            "index": 0,
            "function": {"arguments": "ab"},
        },
        {
            "index": 1,
            "function": {"arguments": "xy"},
        },
    ]
