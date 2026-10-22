from __future__ import annotations

import re
from typing import Any

from jiter import from_json

# Only extensions that jiter can safely omit in partial_mode=True. Unicode
# escapes use the full parser, including incomplete and unpaired surrogates.
_STRING_EXTENSION = re.compile(r'[^"\\\x00-\x1f\ud800-\udfff]*(?:\\["\\/bfnrt][^"\\\x00-\x1f\ud800-\udfff]*)*(\\)?\Z')
_STRING_BOUNDARY = re.compile(r'\\[\s\S]?|"')


class PartialJSONParser:
    """Reparse a fixed prefix while an unfinished JSON string grows."""

    def __init__(self) -> None:
        self._length = 0
        self._in_string = False
        self._escaped = False
        self._unicode_escape = False
        self._prefix = b""

    def parse(self, value: str) -> Any:
        delta = value[self._length :]
        if self._escaped:
            delta = "\\" + delta

        if self._in_string and not self._unicode_escape:
            extension = _STRING_EXTENSION.fullmatch(delta)
            if extension is not None:
                self._length = len(value)
                self._escaped = extension[1] is not None
                # Parse again rather than reuse a mutable dict/list from an
                # earlier event. The unfinished string contributes no value.
                return from_json(self._prefix, partial_mode=True)

        raw = value.encode("utf-8")
        parsed = from_json(raw, partial_mode=True)
        for match in _STRING_BOUNDARY.finditer(delta):
            token = match[0]
            if token == '"':
                self._in_string = not self._in_string
                self._unicode_escape = False
            elif self._in_string and token == "\\u":
                self._unicode_escape = True
            self._escaped = self._in_string and token == "\\"
        self._length = len(value)
        self._prefix = raw if self._in_string and not self._unicode_escape else b""
        return parsed
