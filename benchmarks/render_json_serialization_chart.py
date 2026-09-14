"""Render paired JSON-serializer benchmark distributions as theme-aware SVGs."""

from __future__ import annotations

import html
import json
import argparse
from typing import Any, Literal, cast
from pathlib import Path
from collections.abc import Mapping, Iterable

ThemeName = Literal["dark", "light"]

_THEMES: dict[ThemeName, dict[str, str]] = {
    "light": {
        "background": "#ffffff",
        "panel": "#f8fafc",
        "border": "#cbd5e1",
        "grid": "#cbd5e1",
        "text": "#0f172a",
        "muted": "#475569",
        "stdlib": "#2563eb",
        "orjson": "#16a34a",
    },
    "dark": {
        "background": "#0d1117",
        "panel": "#161b22",
        "border": "#30363d",
        "grid": "#30363d",
        "text": "#f0f6fc",
        "muted": "#8b949e",
        "stdlib": "#60a5fa",
        "orjson": "#34d399",
    },
}

_SERIALIZER_ORDER = ("stdlib", "orjson")
_WIDTH = 1320
_HEIGHT = 580
_PLOT_TOP = 158
_PLOT_HEIGHT = 280
_PANEL_WIDTH = 370
_PANEL_GAP = 20
_PANEL_LEFT = 90


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _number(value: object) -> float:
    if not isinstance(value, (int, float)):
        raise ValueError(f"Expected a numeric benchmark statistic, got {value!r}")
    return float(value)


def _benchmark_records(payload: Mapping[str, Any]) -> dict[int, dict[str, dict[str, float]]]:
    records: dict[int, dict[str, dict[str, float]]] = {}
    benchmarks = payload.get("benchmarks")
    if not isinstance(benchmarks, list):
        raise ValueError("pytest-benchmark JSON is missing its benchmarks list")

    for item in benchmarks:
        if not isinstance(item, Mapping):
            continue
        params = item.get("params")
        stats = item.get("stats")
        if not isinstance(params, Mapping) or not isinstance(stats, Mapping):
            continue
        serializer = params.get("serializer_name")
        target_size_bytes = params.get("target_size_bytes")
        if serializer not in _SERIALIZER_ORDER or not isinstance(target_size_bytes, int):
            continue
        records.setdefault(target_size_bytes, {})[serializer] = {
            statistic: _number(stats.get(statistic))
            for statistic in ("min", "q1", "median", "q3", "max", "mean")
        }

    if not records:
        raise ValueError("No JSON serializer benchmark results were found")
    for target_size_bytes, serializers in records.items():
        if set(serializers) != set(_SERIALIZER_ORDER):
            raise ValueError(f"Missing serializer result for {target_size_bytes} byte payload")
    return records


def _payload_label(target_size_bytes: int) -> str:
    if target_size_bytes == 16_000:
        return "18 KB encoded payload"
    if target_size_bytes == 256_000:
        return "289 KB encoded payload"
    if target_size_bytes == 1_000_000:
        return "1.13 MB encoded payload"
    return f"{target_size_bytes / 1_000_000:.2f} MB encoded payload"


def _duration(value_seconds: float) -> str:
    microseconds = value_seconds * 1_000_000
    if microseconds < 1_000:
        return f"{microseconds:.1f} us"
    return f"{microseconds / 1_000:.2f} ms"


def _ticks(lower: float, upper: float) -> Iterable[float]:
    for step in range(5):
        yield lower + (upper - lower) * step / 4


def _y(value: float, lower: float, upper: float) -> float:
    return _PLOT_TOP + _PLOT_HEIGHT - (value - lower) / (upper - lower) * _PLOT_HEIGHT


def _svg_text(x: float, y: float, text: str, css_class: str, anchor: str = "start") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{css_class}" text-anchor="{anchor}">{_escape(text)}</text>'


def _distribution(
    *,
    center: float,
    statistics: Mapping[str, float],
    color: str,
    lower: float,
    upper: float,
) -> str:
    minimum = _y(statistics["min"], lower, upper)
    q1 = _y(statistics["q1"], lower, upper)
    median = _y(statistics["median"], lower, upper)
    q3 = _y(statistics["q3"], lower, upper)
    maximum = _y(statistics["max"], lower, upper)
    mean = _y(statistics["mean"], lower, upper)
    box_width = 104
    cap_width = 44
    return "\n".join(
        (
            f'<line x1="{center:.1f}" y1="{maximum:.1f}" x2="{center:.1f}" y2="{q3:.1f}" class="whisker" />',
            f'<line x1="{center:.1f}" y1="{q1:.1f}" x2="{center:.1f}" y2="{minimum:.1f}" class="whisker" />',
            f'<line x1="{center - cap_width / 2:.1f}" y1="{maximum:.1f}" x2="{center + cap_width / 2:.1f}" y2="{maximum:.1f}" class="whisker" />',
            f'<line x1="{center - cap_width / 2:.1f}" y1="{minimum:.1f}" x2="{center + cap_width / 2:.1f}" y2="{minimum:.1f}" class="whisker" />',
            f'<rect x="{center - box_width / 2:.1f}" y="{q3:.1f}" width="{box_width}" height="{q1 - q3:.1f}" fill="{color}" fill-opacity="0.28" stroke="{color}" stroke-width="2" />',
            f'<line x1="{center - box_width / 2:.1f}" y1="{median:.1f}" x2="{center + box_width / 2:.1f}" y2="{median:.1f}" stroke="{color}" stroke-width="3" />',
            f'<circle cx="{center:.1f}" cy="{mean:.1f}" r="5" fill="{color}" stroke="currentColor" stroke-width="1.5" />',
        )
    )


def render_svg(records: Mapping[int, Mapping[str, Mapping[str, float]]], theme_name: ThemeName) -> str:
    theme = _THEMES[theme_name]
    panels: list[str] = []
    for panel_index, (target_size_bytes, serializers) in enumerate(sorted(records.items())):
        x = _PANEL_LEFT + panel_index * (_PANEL_WIDTH + _PANEL_GAP)
        values = [value for serializer in serializers.values() for value in serializer.values()]
        minimum = min(values)
        maximum = max(values)
        padding = max((maximum - minimum) * 0.12, maximum * 0.03)
        lower = max(0.0, minimum - padding)
        upper = maximum + padding
        tick_lines: list[str] = []
        for tick in _ticks(lower, upper):
            y = _y(tick, lower, upper)
            tick_lines.extend(
                (
                    f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + _PANEL_WIDTH:.1f}" y2="{y:.1f}" class="grid" />',
                    _svg_text(x - 8, y + 4, _duration(tick), "axis", "end"),
                )
            )
        stdlib_median = serializers["stdlib"]["median"]
        orjson_median = serializers["orjson"]["median"]
        speedup = stdlib_median / orjson_median
        centers = {"stdlib": x + 118, "orjson": x + 272}
        distributions = "\n".join(
            _distribution(
                center=centers[name],
                statistics=serializers[name],
                color=theme[name],
                lower=lower,
                upper=upper,
            )
            for name in _SERIALIZER_ORDER
        )
        labels = "\n".join(
            (
                _svg_text(centers["stdlib"], _PLOT_TOP + _PLOT_HEIGHT + 28, "stdlib json", "series stdlib", "middle"),
                _svg_text(centers["orjson"], _PLOT_TOP + _PLOT_HEIGHT + 28, "orjson", "series orjson", "middle"),
                _svg_text(centers["stdlib"], _PLOT_TOP + _PLOT_HEIGHT + 50, f"median {_duration(stdlib_median)}", "detail", "middle"),
                _svg_text(centers["orjson"], _PLOT_TOP + _PLOT_HEIGHT + 50, f"median {_duration(orjson_median)}", "detail", "middle"),
            )
        )
        panels.append(
            "\n".join(
                (
                    f'<rect x="{x:.1f}" y="122" width="{_PANEL_WIDTH}" height="350" rx="10" class="panel" />',
                    _svg_text(x + 18, 150, _payload_label(target_size_bytes), "panel-title"),
                    _svg_text(x + _PANEL_WIDTH - 18, 150, f"{speedup:.2f}x faster", "speedup", "end"),
                    *tick_lines,
                    distributions,
                    labels,
                )
            )
        )

    rendered_panels = "\n  ".join(panels)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{_WIDTH}" height="{_HEIGHT}" viewBox="0 0 {_WIDTH} {_HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">JSON serializer benchmark distributions</title>
  <desc id="desc">Paired stdlib JSON and orjson distributions for three encoded payload sizes. Boxes show the interquartile range, horizontal lines show the median, whiskers show minimum and maximum, and dots show the mean.</desc>
  <style>
    svg {{ background: {theme["background"]}; color: {theme["text"]}; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .title {{ fill: {theme["text"]}; font-size: 25px; font-weight: 700; }}
    .subtitle, .detail, .axis {{ fill: {theme["muted"]}; font-size: 13px; }}
    .panel {{ fill: {theme["panel"]}; stroke: {theme["border"]}; stroke-width: 1; }}
    .panel-title {{ fill: {theme["text"]}; font-size: 16px; font-weight: 700; }}
    .speedup {{ fill: {theme["orjson"]}; font-size: 15px; font-weight: 700; }}
    .grid {{ stroke: {theme["grid"]}; stroke-width: 1; stroke-dasharray: 3 5; }}
    .whisker {{ stroke: currentColor; stroke-width: 1.5; }}
    .series {{ font-size: 14px; font-weight: 700; }}
    .stdlib {{ fill: {theme["stdlib"]}; }}
    .orjson {{ fill: {theme["orjson"]}; }}
  </style>
  <rect width="100%" height="100%" fill="{theme["background"]}" />
  <text x="40" y="48" class="title">Request-body JSON serialization distribution</text>
  <text x="40" y="74" class="subtitle">Box = interquartile range · line = median · whiskers = min/max · dot = mean</text>
  <rect x="985" y="37" width="14" height="14" rx="3" fill="{theme["stdlib"]}" />
  <text x="1007" y="49" class="subtitle">stdlib json</text>
  <rect x="1130" y="37" width="14" height="14" rx="3" fill="{theme["orjson"]}" />
  <text x="1152" y="49" class="subtitle">orjson</text>
  {rendered_panels}
  <text x="40" y="534" class="subtitle">Synthetic Pydantic chat-style payloads · serializer CPU only · lower is better</text>
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="pytest-benchmark JSON output")
    parser.add_argument("--output-dir", type=Path, required=True, help="directory for themed SVGs")
    args = parser.parse_args()
    records = _benchmark_records(cast(Mapping[str, Any], json.loads(args.input.read_text())))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for theme_name in _THEMES:
        output = args.output_dir / f"json-serialization-{theme_name}.svg"
        output.write_text(render_svg(records, theme_name))


if __name__ == "__main__":
    main()
