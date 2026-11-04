# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["AudioModel"]

AudioModel: TypeAlias = Literal[
    "whisper-1",
    "gpt-transcribe",
    "gpt-4o-transcribe",
    "gpt-4o-mini-transcribe",
    "gpt-4o-mini-transcribe-2025-12-15",
    "gpt-4o-transcribe-diarize",
]
"""Deprecated values:

- "whisper-1", "gpt-4o-transcribe", "gpt-4o-mini-transcribe",
  "gpt-4o-mini-transcribe-2025-12-15", "gpt-4o-transcribe-diarize": Announced
  shutdown date: 2027-02-26. See
  https://developers.openai.com/api/docs/deprecations for details and
  recommended replacements.
"""
