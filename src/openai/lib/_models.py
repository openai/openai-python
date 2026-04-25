"""Convenience helpers for inspecting OpenAI model capabilities.

This module is hand-maintained (not generated from the OpenAPI spec) because the
capability matrix is documented behaviour rather than schema. When OpenAI ships
a new model family, the registry in this file should be updated to match.

The canonical source for reasoning-effort behaviour is the docstring on the
``Reasoning.effort`` parameter in ``src/openai/types/shared/reasoning.py``.

Example:
    >>> from openai import get_model_capabilities
    >>> caps = get_model_capabilities("gpt-5.4-mini")
    >>> caps.supports_reasoning
    True
    >>> caps.reasoning_effort_options
    ('none', 'low', 'medium', 'high', 'xhigh')
    >>> get_model_capabilities("gpt-4.1").supports_reasoning
    False
"""

from __future__ import annotations

import re
from typing import Any, Tuple, Optional
from dataclasses import dataclass

from ..types.shared.reasoning_effort import ReasoningEffort

__all__ = ["ModelCapabilities", "get_model_capabilities"]


@dataclass(frozen=True)
class ModelCapabilities:
    """Static capability metadata for an OpenAI model.

    Returned by :func:`get_model_capabilities`. All fields reflect the
    *documented* behaviour of the model when called via the Chat Completions
    or Responses APIs. They are not derived from a server-side source, so
    edge cases (private deployments, beta flags, future model variants) may
    differ.
    """

    family: str
    """The model family identifier this capability set was matched against
    (e.g. ``"gpt-5.4"``, ``"gpt-4o"``).

    Useful when dispatching on the family in addition to the exact model name."""

    supports_temperature: bool
    """Whether the model accepts the ``temperature`` parameter.

    Note: gpt-5.x reasoning models reject ``temperature`` whenever
    ``reasoning_effort`` is anything other than ``"none"``. The conservative
    default returned here is ``False`` for reasoning models, matching the
    behaviour you should use unless you have explicitly opted into a
    ``-chat-latest`` variant.
    """

    supports_reasoning: bool
    """Whether the model accepts the ``reasoning`` parameter (Responses API)
    or ``reasoning_effort`` (Chat Completions)."""

    reasoning_effort_options: Optional[Tuple[ReasoningEffort, ...]]
    """Valid values for ``reasoning.effort``.

    ``None`` if the model does not support reasoning. Otherwise a tuple of
    valid effort literals, in order of increasing intensity."""


def _caps(
    family: str,
    *,
    supports_temperature: bool,
    supports_reasoning: bool,
    reasoning_effort_options: Optional[Tuple[ReasoningEffort, ...]],
) -> ModelCapabilities:
    return ModelCapabilities(
        family=family,
        supports_temperature=supports_temperature,
        supports_reasoning=supports_reasoning,
        reasoning_effort_options=reasoning_effort_options,
    )


# ---------------------------------------------------------------------------
# Family registry.
#
# Entries are matched by longest *segment* prefix against the model string
# (i.e. the registered prefix must either equal the model exactly or be
# followed by a `-`), with chat / search variants checked via the suffix test
# in `get_model_capabilities`.
#
# When OpenAI ships a new family, add an entry here. Order within this tuple
# does not matter; the lookup picks the longest matching prefix.
# ---------------------------------------------------------------------------

# Effort scales reused across families. These mirror the prose in
# `src/openai/types/shared/reasoning.py`:
#
#   - All models *before* gpt-5.1 default to medium and do NOT support `none`.
#     gpt-5 base accepts `minimal/low/medium/high`.
#   - gpt-5.1 supports `none/low/medium/high` (no `minimal`).
#   - `xhigh` is supported for models *after* gpt-5.1-codex-max, i.e.
#     gpt-5.2 onward, on top of the gpt-5.1 effort scale.
#   - gpt-5-pro defaults to and only supports `high`.
_EFFORT_O_SERIES: Tuple[ReasoningEffort, ...] = ("low", "medium", "high")
_EFFORT_GPT5_BASE: Tuple[ReasoningEffort, ...] = ("minimal", "low", "medium", "high")
_EFFORT_GPT5_1: Tuple[ReasoningEffort, ...] = ("none", "low", "medium", "high")
_EFFORT_GPT5_2_PLUS: Tuple[ReasoningEffort, ...] = ("none", "low", "medium", "high", "xhigh")
_EFFORT_GPT5_PRO: Tuple[ReasoningEffort, ...] = ("high",)


_FAMILIES: Tuple[ModelCapabilities, ...] = (
    # gpt-5.x reasoning models. Temperature is rejected unless you use a
    # `-chat-latest` variant or set `reasoning_effort="none"`.
    #
    # gpt-5-pro is a high-only reasoning model and must be registered as its
    # own family so longest-prefix matching beats the generic `gpt-5`.
    _caps("gpt-5-pro", supports_temperature=False, supports_reasoning=True, reasoning_effort_options=_EFFORT_GPT5_PRO),
    _caps("gpt-5.4", supports_temperature=False, supports_reasoning=True, reasoning_effort_options=_EFFORT_GPT5_2_PLUS),
    _caps("gpt-5.3", supports_temperature=False, supports_reasoning=True, reasoning_effort_options=_EFFORT_GPT5_2_PLUS),
    _caps("gpt-5.2", supports_temperature=False, supports_reasoning=True, reasoning_effort_options=_EFFORT_GPT5_2_PLUS),
    _caps("gpt-5.1", supports_temperature=False, supports_reasoning=True, reasoning_effort_options=_EFFORT_GPT5_1),
    _caps("gpt-5", supports_temperature=False, supports_reasoning=True, reasoning_effort_options=_EFFORT_GPT5_BASE),
    # Classic chat families.
    _caps("gpt-4.1", supports_temperature=True, supports_reasoning=False, reasoning_effort_options=None),
    _caps("gpt-4o", supports_temperature=True, supports_reasoning=False, reasoning_effort_options=None),
    _caps("gpt-4-turbo", supports_temperature=True, supports_reasoning=False, reasoning_effort_options=None),
    _caps("gpt-4", supports_temperature=True, supports_reasoning=False, reasoning_effort_options=None),
    _caps("gpt-3.5", supports_temperature=True, supports_reasoning=False, reasoning_effort_options=None),
    _caps("chatgpt-4o-latest", supports_temperature=True, supports_reasoning=False, reasoning_effort_options=None),
    # o-series reasoning models.
    _caps("o4-mini", supports_temperature=False, supports_reasoning=True, reasoning_effort_options=_EFFORT_O_SERIES),
    _caps("o3-pro", supports_temperature=False, supports_reasoning=True, reasoning_effort_options=_EFFORT_O_SERIES),
    _caps("o3-mini", supports_temperature=False, supports_reasoning=True, reasoning_effort_options=_EFFORT_O_SERIES),
    _caps(
        "o3-deep-research",
        supports_temperature=False,
        supports_reasoning=True,
        reasoning_effort_options=_EFFORT_O_SERIES,
    ),
    _caps("o3", supports_temperature=False, supports_reasoning=True, reasoning_effort_options=_EFFORT_O_SERIES),
    _caps("o1-pro", supports_temperature=False, supports_reasoning=True, reasoning_effort_options=_EFFORT_O_SERIES),
    _caps("o1-mini", supports_temperature=False, supports_reasoning=True, reasoning_effort_options=_EFFORT_O_SERIES),
    # o1-preview rejects temperature but doesn't expose the effort parameter.
    # Must be matched before the broader "o1" prefix via longest-prefix logic.
    _caps("o1-preview", supports_temperature=False, supports_reasoning=False, reasoning_effort_options=None),
    _caps("o1", supports_temperature=False, supports_reasoning=True, reasoning_effort_options=_EFFORT_O_SERIES),
    _caps(
        "codex-mini",
        supports_temperature=True,
        supports_reasoning=True,
        reasoning_effort_options=_EFFORT_O_SERIES,
    ),
    _caps(
        "computer-use-preview",
        supports_temperature=True,
        supports_reasoning=False,
        reasoning_effort_options=None,
    ),
)


# Matches `*-chat-latest` and `*-search-preview` (with an optional trailing
# `-YYYY-MM-DD` snapshot date), e.g. `gpt-4o-search-preview-2025-03-11`.
# These variants behave like classic chat models regardless of family.
_CHAT_VARIANT_RE = re.compile(r"-(?:chat-latest|search-preview)(?:-\d{4}-\d{2}-\d{2})?$")


def _matches_family(model: str, family: str) -> bool:
    """Match ``model`` against a family prefix at a segment boundary.

    A model matches when it equals the family exactly or extends it with a
    ``-`` separator. This prevents collisions like ``gpt-5.10`` being
    misclassified as ``gpt-5.1``.
    """
    if model == family:
        return True
    return model.startswith(family + "-")


def get_model_capabilities(model: str) -> Optional[ModelCapabilities]:
    """Return capability metadata for ``model``, or ``None`` if unknown.

    The lookup is purely string-based: it does not call the OpenAI API. That
    means it works in offline contexts (tests, build scripts, UIs that need to
    decide which controls to render) but is only as fresh as this module's
    registry. New model families need a corresponding entry here.

    Matching is segment-aware: the registered prefix must either equal the
    model exactly or be followed by a ``-`` separator. ``"gpt-5.10"`` will
    therefore *not* match the ``gpt-5.1`` family and ``"o1-previewed"`` will
    not match ``o1-preview``; both fall through to ``None`` so callers treat
    them as unknown.

    Args:
        model: A model identifier such as ``"gpt-5.4-mini"`` or
            ``"gpt-4o-2024-08-06"``. Date suffixes and size variants
            (``-mini``, ``-nano``, ``-pro``) are handled automatically by
            longest-prefix matching.

    Returns:
        A :class:`ModelCapabilities` describing the model, or ``None`` if no
        registered family matches. Callers should treat ``None`` as
        "capability unknown" and fall back to feature-detecting at request
        time (i.e. send the parameter and handle a 400 response).

    Example:
        >>> get_model_capabilities("gpt-5.4-mini").reasoning_effort_options
        ('none', 'low', 'medium', 'high', 'xhigh')
        >>> get_model_capabilities("gpt-5-chat-latest").supports_temperature
        True
        >>> get_model_capabilities("gpt-5").supports_temperature
        False
        >>> get_model_capabilities("gpt-5-pro").reasoning_effort_options
        ('high',)
        >>> get_model_capabilities("gpt-5.10") is None
        True
        >>> get_model_capabilities("nonexistent-model") is None
        True
    """
    # Runtime guard: callers may pass arbitrary values from config files, so
    # we accept Any at the boundary and reject non-strings explicitly rather
    # than relying on the type checker alone.
    candidate: Any = model
    if not isinstance(candidate, str) or not candidate:
        return None

    # Longest matching family wins so that "gpt-5.4" beats "gpt-5", and
    # "o1-pro" beats "o1". Segment boundary check rejects things like
    # "gpt-5.10" claiming to be "gpt-5.1".
    best: Optional[ModelCapabilities] = None
    for entry in _FAMILIES:
        if not _matches_family(candidate, entry.family):
            continue
        if best is None or len(entry.family) > len(best.family):
            best = entry

    if best is None:
        return None

    # Chat / search variants override family defaults: gpt-5-chat-latest is a
    # non-reasoning model even though gpt-5* normally is one. We still report
    # the family so callers can group e.g. "gpt-5.2-chat-latest" with
    # "gpt-5.2". The regex tolerates a trailing date snapshot like
    # `-2025-03-11` so dated variants like `gpt-4o-search-preview-2025-03-11`
    # are recognized too.
    if _CHAT_VARIANT_RE.search(candidate):
        return ModelCapabilities(
            family=best.family,
            supports_temperature=True,
            supports_reasoning=False,
            reasoning_effort_options=None,
        )

    return best
