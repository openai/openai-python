from __future__ import annotations

import pytest

import openai
from openai.lib._models import ModelCapabilities, get_model_capabilities


class TestGpt5Family:
    def test_gpt_5_uses_minimal_low_medium_high(self) -> None:
        caps = get_model_capabilities("gpt-5")
        assert caps is not None
        assert caps.family == "gpt-5"
        assert caps.supports_reasoning is True
        assert caps.supports_temperature is False
        assert caps.reasoning_effort_options == ("minimal", "low", "medium", "high")

    def test_gpt_5_size_variants_resolve_to_same_family(self) -> None:
        for size in ("gpt-5", "gpt-5-mini", "gpt-5-nano"):
            caps = get_model_capabilities(size)
            assert caps is not None, size
            assert caps.family == "gpt-5"

    def test_gpt_5_dated_snapshot(self) -> None:
        caps = get_model_capabilities("gpt-5-mini-2025-08-07")
        assert caps is not None
        assert caps.family == "gpt-5"
        assert caps.supports_reasoning is True

    def test_gpt_5_chat_latest_is_non_reasoning(self) -> None:
        caps = get_model_capabilities("gpt-5-chat-latest")
        assert caps is not None
        # The family is still gpt-5 so callers can group variants together,
        # but the capabilities mirror a classic chat model.
        assert caps.family == "gpt-5"
        assert caps.supports_temperature is True
        assert caps.supports_reasoning is False
        assert caps.reasoning_effort_options is None


class TestGpt51Family:
    def test_gpt_5_1_drops_minimal_adds_none(self) -> None:
        # Per src/openai/types/shared/reasoning.py the supported gpt-5.1
        # effort values are none/low/medium/high. `minimal` was removed and
        # would trigger 400 responses if surfaced in a UI.
        caps = get_model_capabilities("gpt-5.1")
        assert caps is not None
        assert caps.family == "gpt-5.1"
        assert caps.reasoning_effort_options == ("none", "low", "medium", "high")
        assert "minimal" not in (caps.reasoning_effort_options or ())

    def test_gpt_5_1_codex(self) -> None:
        caps = get_model_capabilities("gpt-5.1-codex")
        assert caps is not None
        assert caps.family == "gpt-5.1"

    def test_gpt_5_1_codex_max(self) -> None:
        # gpt-5.1-codex-max is the boundary referenced in the SDK docs:
        # `xhigh` is supported for models *after* this one. So it should
        # still match the gpt-5.1 family (no xhigh).
        caps = get_model_capabilities("gpt-5.1-codex-max")
        assert caps is not None
        assert caps.family == "gpt-5.1"
        assert "xhigh" not in (caps.reasoning_effort_options or ())


class TestGpt52PlusFamilies:
    def test_gpt_5_2_supports_xhigh(self) -> None:
        # Per the SDK docstring, `xhigh` is supported for all models *after*
        # gpt-5.1-codex-max, which means gpt-5.2 onward.
        caps = get_model_capabilities("gpt-5.2")
        assert caps is not None
        assert caps.family == "gpt-5.2"
        assert caps.reasoning_effort_options == ("none", "low", "medium", "high", "xhigh")

    def test_gpt_5_2_pro(self) -> None:
        caps = get_model_capabilities("gpt-5.2-pro")
        assert caps is not None
        assert caps.family == "gpt-5.2"


class TestGpt5ProFamily:
    def test_gpt_5_pro_only_supports_high(self) -> None:
        # Per the SDK docs, gpt-5-pro defaults to (and only supports) `high`.
        caps = get_model_capabilities("gpt-5-pro")
        assert caps is not None
        assert caps.family == "gpt-5-pro"
        assert caps.supports_reasoning is True
        assert caps.reasoning_effort_options == ("high",)

    def test_gpt_5_pro_dated_snapshot(self) -> None:
        caps = get_model_capabilities("gpt-5-pro-2025-10-06")
        assert caps is not None
        assert caps.family == "gpt-5-pro"
        assert caps.reasoning_effort_options == ("high",)


class TestGpt54Family:
    def test_gpt_5_4_full_effort_scale(self) -> None:
        caps = get_model_capabilities("gpt-5.4")
        assert caps is not None
        assert caps.family == "gpt-5.4"
        assert caps.reasoning_effort_options == ("none", "low", "medium", "high", "xhigh")
        assert "minimal" not in (caps.reasoning_effort_options or ())

    def test_gpt_5_4_size_variants(self) -> None:
        for size in ("gpt-5.4", "gpt-5.4-mini", "gpt-5.4-nano"):
            caps = get_model_capabilities(size)
            assert caps is not None, size
            assert caps.family == "gpt-5.4"
            assert "xhigh" in (caps.reasoning_effort_options or ())

    def test_gpt_5_4_dated_snapshot(self) -> None:
        caps = get_model_capabilities("gpt-5.4-mini-2026-03-17")
        assert caps is not None
        assert caps.family == "gpt-5.4"


class TestGpt4Family:
    def test_gpt_4_1_supports_temperature_no_reasoning(self) -> None:
        caps = get_model_capabilities("gpt-4.1")
        assert caps is not None
        assert caps.family == "gpt-4.1"
        assert caps.supports_temperature is True
        assert caps.supports_reasoning is False
        assert caps.reasoning_effort_options is None

    def test_gpt_4_1_size_variants(self) -> None:
        for size in ("gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano"):
            caps = get_model_capabilities(size)
            assert caps is not None, size
            assert caps.family == "gpt-4.1"

    def test_gpt_4o_supports_temperature_no_reasoning(self) -> None:
        caps = get_model_capabilities("gpt-4o")
        assert caps is not None
        assert caps.family == "gpt-4o"
        assert caps.supports_temperature is True
        assert caps.supports_reasoning is False

    def test_gpt_4o_search_preview_is_chat_variant(self) -> None:
        caps = get_model_capabilities("gpt-4o-search-preview")
        assert caps is not None
        assert caps.supports_temperature is True
        assert caps.supports_reasoning is False

    def test_gpt_4_turbo(self) -> None:
        caps = get_model_capabilities("gpt-4-turbo")
        assert caps is not None
        assert caps.family == "gpt-4-turbo"
        assert caps.supports_temperature is True

    def test_gpt_4_base(self) -> None:
        caps = get_model_capabilities("gpt-4")
        assert caps is not None
        assert caps.family == "gpt-4"

    def test_gpt_3_5_turbo(self) -> None:
        caps = get_model_capabilities("gpt-3.5-turbo")
        assert caps is not None
        assert caps.family == "gpt-3.5"
        assert caps.supports_temperature is True
        assert caps.supports_reasoning is False


class TestOSeriesFamily:
    def test_o1_supports_reasoning(self) -> None:
        caps = get_model_capabilities("o1")
        assert caps is not None
        assert caps.supports_reasoning is True
        assert caps.supports_temperature is False
        assert caps.reasoning_effort_options == ("low", "medium", "high")

    def test_o1_preview_does_not_expose_effort(self) -> None:
        # o1-preview rejects temperature but doesn't expose the effort
        # parameter. It must be matched before the broader "o1" prefix.
        caps = get_model_capabilities("o1-preview")
        assert caps is not None
        assert caps.supports_reasoning is False
        assert caps.supports_temperature is False

    def test_o1_mini_uses_o_series_effort_scale(self) -> None:
        caps = get_model_capabilities("o1-mini")
        assert caps is not None
        assert caps.reasoning_effort_options == ("low", "medium", "high")

    def test_o3_pro_matches_before_o3(self) -> None:
        caps = get_model_capabilities("o3-pro")
        assert caps is not None
        assert caps.family == "o3-pro"

    def test_o3_dated(self) -> None:
        caps = get_model_capabilities("o3-2025-04-16")
        assert caps is not None
        assert caps.family == "o3"
        assert caps.supports_reasoning is True

    def test_o4_mini(self) -> None:
        caps = get_model_capabilities("o4-mini")
        assert caps is not None
        assert caps.supports_reasoning is True


class TestBoundaryMatching:
    """Family lookup must respect segment boundaries.

    A registered prefix should only match the model when the prefix either
    equals the model exactly or is followed by ``-``. Without this, a future
    model name like ``gpt-5.10`` would silently impersonate ``gpt-5.1``.
    """

    @pytest.mark.parametrize(
        "model",
        [
            "gpt-5.10",  # version typo / future model: must NOT match gpt-5.1
            "gpt-5.10-mini",
            "gpt-5.1foo",
            "o1-previewed",  # near-typo of o1-preview
            "o1-previews",
        ],
    )
    def test_boundary_collisions_do_not_misclassify(self, model: str) -> None:
        # Either we return None (no match) or we match a strictly different
        # family (e.g. `gpt-5.10` could match `gpt-5` segment-wise -- in that
        # case we want it to NOT claim to be gpt-5.1).
        caps = get_model_capabilities(model)
        if caps is not None:
            assert caps.family != "gpt-5.1", model
            assert caps.family != "o1-preview", model

    def test_gpt_5_10_does_not_match_gpt_5_1(self) -> None:
        # `gpt-5.10` is hypothetical, but the lookup must not classify it as
        # gpt-5.1 just because of `startswith`. Today we'd expect None until
        # a 5.10 family is registered.
        assert get_model_capabilities("gpt-5.10") is None

    def test_o1_previewed_does_not_match_o1_preview(self) -> None:
        # Without the boundary check, `o1-previewed` would be tagged as
        # o1-preview (which has supports_reasoning=False), masking what is
        # really an unknown model.
        caps = get_model_capabilities("o1-previewed")
        if caps is not None:
            assert caps.family != "o1-preview"

    def test_exact_match_still_works(self) -> None:
        # Sanity: removing collisions must not break the exact-match path.
        for model in ("gpt-5.1", "o1-preview", "chatgpt-4o-latest", "gpt-5-pro"):
            assert get_model_capabilities(model) is not None, model

    def test_dated_search_preview_still_recognized_as_chat_variant(self) -> None:
        # `gpt-4o-search-preview-2025-03-11` should still count as a chat
        # variant despite the trailing date snapshot. The previous suffix
        # check (`endswith("-search-preview")`) silently regressed on dated
        # models.
        caps = get_model_capabilities("gpt-4o-search-preview-2025-03-11")
        assert caps is not None
        assert caps.supports_temperature is True
        assert caps.supports_reasoning is False

    def test_dated_chat_latest_still_recognized_as_chat_variant(self) -> None:
        caps = get_model_capabilities("gpt-5.2-chat-latest-2025-12-11")
        assert caps is not None
        assert caps.supports_temperature is True
        assert caps.supports_reasoning is False
        # Family should still be reported as the underlying gpt-5.2
        assert caps.family == "gpt-5.2"


class TestUnknownAndEdgeCases:
    def test_unknown_model_returns_none(self) -> None:
        assert get_model_capabilities("nonexistent-model") is None

    def test_empty_string_returns_none(self) -> None:
        assert get_model_capabilities("") is None

    @pytest.mark.parametrize("bad_input", [None, 123, [], {}])
    def test_non_string_input_returns_none(self, bad_input: object) -> None:
        # Runtime guard: callers may pass arbitrary values from config files.
        assert get_model_capabilities(bad_input) is None  # type: ignore[arg-type]

    def test_returns_model_capabilities_instance(self) -> None:
        caps = get_model_capabilities("gpt-5")
        assert isinstance(caps, ModelCapabilities)

    def test_capabilities_are_frozen(self) -> None:
        from dataclasses import FrozenInstanceError

        caps = get_model_capabilities("gpt-5")
        assert caps is not None
        with pytest.raises(FrozenInstanceError):
            caps.family = "mutated"  # type: ignore[misc]


class TestExports:
    def test_top_level_export(self) -> None:
        # Documented public surface: importable directly from `openai`.
        assert openai.get_model_capabilities is get_model_capabilities
        assert openai.ModelCapabilities is ModelCapabilities

    def test_importable_from_openai_lib(self) -> None:
        from openai.lib import (
            ModelCapabilities as LibCaps,
            get_model_capabilities as lib_func,
        )

        assert LibCaps is ModelCapabilities
        assert lib_func is get_model_capabilities


class TestRealisticUsage:
    """The use case from the issue: dispatching parameters by model."""

    def test_can_route_temperature_decision(self) -> None:
        def should_send_temperature(model: str) -> bool:
            caps = get_model_capabilities(model)
            return caps.supports_temperature if caps else True  # default permissive

        assert should_send_temperature("gpt-4o") is True
        assert should_send_temperature("gpt-4.1-mini") is True
        assert should_send_temperature("gpt-5") is False
        assert should_send_temperature("gpt-5.4-nano") is False
        assert should_send_temperature("o3-mini") is False
        # Chat variants accept temperature even within reasoning families
        assert should_send_temperature("gpt-5-chat-latest") is True

    def test_can_build_effort_dropdown(self) -> None:
        def effort_options(model: str) -> tuple[str, ...]:
            caps = get_model_capabilities(model)
            if caps is None or caps.reasoning_effort_options is None:
                return ()
            # Filter Nones (since ReasoningEffort is Optional[Literal[...]])
            return tuple(opt for opt in caps.reasoning_effort_options if opt is not None)

        assert effort_options("gpt-5") == ("minimal", "low", "medium", "high")
        assert effort_options("gpt-5.1") == ("none", "low", "medium", "high")
        assert effort_options("gpt-5.4") == (
            "none",
            "low",
            "medium",
            "high",
            "xhigh",
        )
        assert effort_options("gpt-5-pro") == ("high",)
        assert effort_options("gpt-4.1") == ()
        assert effort_options("o3") == ("low", "medium", "high")
