"""Render paired JSON-serializer benchmark distributions as theme-aware SVGs."""

from __future__ import annotations

import html
import json
import argparse
from typing import Any, Literal, cast
from pathlib import Path
from collections.abc import Mapping, Iterable

ThemeName = Literal["dark", "light"]
ChartKind = Literal["request-preparation", "serialization"]

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
_CHARTS: dict[ChartKind, dict[str, str]] = {
    "serialization": {
        "benchmark_prefix": "test_openapi_dumps",
        "title": "Request-body JSON serialization distribution",
        "footer": "Synthetic Pydantic chat-style payloads · serializer CPU only · lower is better",
    },
    "request-preparation": {
        "benchmark_prefix": "test_build_request",
        "title": "SDK REST request-preparation distribution",
        "footer": "Same outbound path used to start REST and streaming requests · excludes network and SSE parsing · lower is better",
    },
}
_WIDTH = 1320
_PLOT_HEIGHT = 280
_PANEL_WIDTH = 370
_PANEL_HEIGHT = 350
_PANEL_GAP = 20
_PANEL_LEFT = 90
_PANEL_TOP = 122
_ROW_GAP = 26
_COLUMNS = 3


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _number(value: object) -> float:
    if not isinstance(value, (int, float)):
        raise ValueError(f"Expected a numeric benchmark statistic, got {value!r}")
    return float(value)


def _benchmark_records(payload: Mapping[str, Any], benchmark_prefix: str) -> dict[int, dict[str, dict[str, float]]]:
    records: dict[int, dict[str, dict[str, float]]] = {}
    benchmarks = payload.get("benchmarks")
    if not isinstance(benchmarks, list):
        raise ValueError("pytest-benchmark JSON is missing its benchmarks list")

    for item in benchmarks:
        if not isinstance(item, Mapping):
            continue
        name = item.get("name")
        if not isinstance(name, str) or not name.startswith(benchmark_prefix):
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
            statistic: _number(stats.get(statistic)) for statistic in ("min", "q1", "median", "q3", "max", "mean")
        }

    if not records:
        raise ValueError(f"No benchmark results matching {benchmark_prefix!r} were found")
    for target_size_bytes, serializers in records.items():
        if set(serializers) != set(_SERIALIZER_ORDER):
            raise ValueError(f"Missing serializer result for {target_size_bytes} byte payload")
    return records


def _payload_label(target_size_bytes: int) -> str:
    if target_size_bytes == 500:
        return "~1 KB tool/stream payload"
    if target_size_bytes == 3_000:
        return "~4 KB short request/response"
    if target_size_bytes == 16_000:
        return "18 KB moderate chat payload"
    if target_size_bytes == 56_000:
        return "64 KB medium context payload"
    if target_size_bytes == 256_000:
        return "289 KB RAG context payload"
    if target_size_bytes == 1_000_000:
        return "1.13 MB large context payload"
    return f"{target_size_bytes / 1_000_000:.2f} MB encoded payload"


def _duration(value_seconds: float) -> str:
    microseconds = value_seconds * 1_000_000
    if microseconds < 1_000:
        return f"{microseconds:.1f} us"
    return f"{microseconds / 1_000:.2f} ms"


def _ticks(lower: float, upper: float) -> Iterable[float]:
    for step in range(5):
        yield lower + (upper - lower) * step / 4


def _y(value: float, lower: float, upper: float, plot_top: float) -> float:
    return plot_top + _PLOT_HEIGHT - (value - lower) / (upper - lower) * _PLOT_HEIGHT


def _svg_text(x: float, y: float, text: str, css_class: str, anchor: str = "start") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{css_class}" text-anchor="{anchor}">{_escape(text)}</text>'


def _distribution(
    *,
    center: float,
    statistics: Mapping[str, float],
    color: str,
    lower: float,
    upper: float,
    plot_top: float,
) -> str:
    minimum = _y(statistics["min"], lower, upper, plot_top)
    q1 = _y(statistics["q1"], lower, upper, plot_top)
    median = _y(statistics["median"], lower, upper, plot_top)
    q3 = _y(statistics["q3"], lower, upper, plot_top)
    maximum = _y(statistics["max"], lower, upper, plot_top)
    mean = _y(statistics["mean"], lower, upper, plot_top)
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


def render_svg(
    records: Mapping[int, Mapping[str, Mapping[str, float]]], theme_name: ThemeName, chart_kind: ChartKind
) -> str:
    theme = _THEMES[theme_name]
    chart = _CHARTS[chart_kind]
    panels: list[str] = []
    for panel_index, (target_size_bytes, serializers) in enumerate(sorted(records.items())):
        row = panel_index // _COLUMNS
        column = panel_index % _COLUMNS
        x = _PANEL_LEFT + column * (_PANEL_WIDTH + _PANEL_GAP)
        panel_top = _PANEL_TOP + row * (_PANEL_HEIGHT + _ROW_GAP)
        plot_top = panel_top + 36
        values = [value for serializer in serializers.values() for value in serializer.values()]
        minimum = min(values)
        maximum = max(values)
        padding = max((maximum - minimum) * 0.12, maximum * 0.03)
        lower = max(0.0, minimum - padding)
        upper = maximum + padding
        tick_lines: list[str] = []
        for tick in _ticks(lower, upper):
            y = _y(tick, lower, upper, plot_top)
            tick_lines.extend(
                (
                    f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + _PANEL_WIDTH:.1f}" y2="{y:.1f}" class="grid" />',
                    _svg_text(x + 8, y + 4, _duration(tick), "axis"),
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
                plot_top=plot_top,
            )
            for name in _SERIALIZER_ORDER
        )
        labels = "\n".join(
            (
                _svg_text(centers["stdlib"], plot_top + _PLOT_HEIGHT + 28, "stdlib json", "series stdlib", "middle"),
                _svg_text(centers["orjson"], plot_top + _PLOT_HEIGHT + 28, "orjson", "series orjson", "middle"),
                _svg_text(
                    centers["stdlib"],
                    plot_top + _PLOT_HEIGHT + 50,
                    f"median {_duration(stdlib_median)}",
                    "detail",
                    "middle",
                ),
                _svg_text(
                    centers["orjson"],
                    plot_top + _PLOT_HEIGHT + 50,
                    f"median {_duration(orjson_median)}",
                    "detail",
                    "middle",
                ),
            )
        )
        panels.append(
            "\n".join(
                (
                    f'<rect x="{x:.1f}" y="{panel_top:.1f}" width="{_PANEL_WIDTH}" height="{_PANEL_HEIGHT}" rx="10" class="panel" />',
                    _svg_text(x + 18, panel_top + 28, _payload_label(target_size_bytes), "panel-title"),
                    _svg_text(x + _PANEL_WIDTH - 18, panel_top + 28, f"{speedup:.2f}x faster", "speedup", "end"),
                    *tick_lines,
                    distributions,
                    labels,
                )
            )
        )

    rendered_panels = "\n  ".join(panels)
    rows = (len(records) + _COLUMNS - 1) // _COLUMNS
    height = _PANEL_TOP + rows * _PANEL_HEIGHT + (rows - 1) * _ROW_GAP + 74
    footer_y = height - 34
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{_WIDTH}" height="{height}" viewBox="0 0 {_WIDTH} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{_escape(chart["title"])}</title>
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
  <text x="40" y="48" class="title">{_escape(chart["title"])}</text>
  <text x="40" y="74" class="subtitle">Box = interquartile range · line = median · whiskers = min/max · dot = mean</text>
  <rect x="985" y="37" width="14" height="14" rx="3" fill="{theme["stdlib"]}" />
  <text x="1007" y="49" class="subtitle">stdlib json</text>
  <rect x="1130" y="37" width="14" height="14" rx="3" fill="{theme["orjson"]}" />
  <text x="1152" y="49" class="subtitle">orjson</text>
  {rendered_panels}
  <text x="40" y="{footer_y}" class="subtitle">{_escape(chart["footer"])}</text>
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chart", choices=tuple(_CHARTS), required=True, help="benchmark group to render")
    parser.add_argument("--input", type=Path, required=True, help="pytest-benchmark JSON output")
    parser.add_argument("--output-dir", type=Path, required=True, help="directory for themed SVGs")
    args = parser.parse_args()
    chart_kind = cast(ChartKind, args.chart)
    records = _benchmark_records(
        cast(Mapping[str, Any], json.loads(args.input.read_text())), _CHARTS[chart_kind]["benchmark_prefix"]
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for theme_name in _THEMES:
        output = args.output_dir / f"{chart_kind}-{theme_name}.svg"
        output.write_text(render_svg(records, theme_name, chart_kind))


if __name__ == "__main__":
    main()
