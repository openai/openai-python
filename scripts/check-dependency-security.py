from __future__ import annotations

import io
import os
import re
import ast
import pathlib
import tokenize
import importlib
import subprocess
from typing import Any, TypeAlias, cast

MarkerClause: TypeAlias = tuple[str, str, str]
MarkerContext: TypeAlias = tuple[MarkerClause, ...]
StableRelease: TypeAlias = tuple[int, tuple[int, ...], int]
PublishedBound: TypeAlias = tuple[str, int, tuple[int, ...], int, bool]
DependencyContext: TypeAlias = tuple[str, str, tuple[str, ...], MarkerContext]
RequirementSource: TypeAlias = tuple[str, str, tuple[str, ...], str]
RequirementMap: TypeAlias = dict[str, set[str]]
ContextRequirements: TypeAlias = dict[DependencyContext, set[str]]
ContextsByName: TypeAlias = dict[str, ContextRequirements]
ContextReplacements: TypeAlias = dict[DependencyContext, ContextRequirements]
ResolutionDomains: TypeAlias = dict[MarkerContext, set[str]]
ResolutionsByName: TypeAlias = dict[str, ResolutionDomains]
tomllib: Any = importlib.import_module("tomllib")

base = os.environ.get("BASE_SHA", "")
if not re.fullmatch(r"[0-9a-f]{40}", base):
    raise SystemExit("Untrusted security-update base commit")
origin = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True).strip()
if origin not in {
    "https://github.com/openai/openai-python",
    "https://github.com/openai/openai-python.git",
    "git@github.com:openai/openai-python.git",
    "ssh://git@github.com/openai/openai-python.git",
}:
    raise SystemExit("Untrusted security-update comparison origin")
subprocess.run(["git", "fetch", "--no-tags", "--depth=1", "origin", base], check=True)


def read_base(path: str) -> dict[str, Any]:
    return cast(dict[str, Any], tomllib.loads(subprocess.check_output(["git", "show", base + ":" + path], text=True)))


def canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_marker_expression(marker: str) -> ast.expr:
    tokens = list(tokenize.generate_tokens(io.StringIO(marker).readline))
    lines = marker.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    replacements: list[tuple[int, int, str]] = []
    for index, token in enumerate(tokens):
        if token.type == tokenize.NAME and token.string == "is":
            raise ValueError("Unsupported Python security dependency marker operator")
        if token.type != tokenize.OP or index + 1 == len(tokens):
            continue
        following = tokens[index + 1]
        if following.type != tokenize.OP or token.end != following.start or following.string != "=":
            continue
        if token.string == "~":
            replacement = "is"
        elif token.string == "==":
            replacement = "is not"
        else:
            continue
        start = offsets[token.start[0] - 1] + token.start[1]
        stop = offsets[following.end[0] - 1] + following.end[1]
        replacements.append((start, stop, replacement))
    for start, stop, replacement in reversed(replacements):
        marker = marker[:start] + replacement + marker[stop:]
    return ast.parse(marker, mode="eval").body


def marker_clause(part: ast.expr) -> MarkerClause:
    if (
        not isinstance(part, ast.Compare)
        or len(part.ops) != 1
        or len(part.comparators) != 1
        or type(part.ops[0])
        not in {ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn, ast.Is, ast.IsNot}
    ):
        raise SystemExit("Ambiguous direct security dependency marker")
    operator = {"Is": "Compatible", "IsNot": "ArbitraryEq"}.get(type(part.ops[0]).__name__, type(part.ops[0]).__name__)
    right = part.comparators[0]
    if isinstance(part.left, ast.Name) and isinstance(right, ast.Constant) and isinstance(right.value, str):
        variable, value = part.left.id, right.value
    elif (
        isinstance(part.left, ast.Constant)
        and isinstance(part.left.value, str)
        and isinstance(right, ast.Name)
        and operator in {"Eq", "NotEq", "Lt", "LtE", "Gt", "GtE", "In", "NotIn"}
    ):
        variable, value = right.id, part.left.value
        operator = {
            "Eq": "Eq",
            "NotEq": "NotEq",
            "Lt": "Gt",
            "LtE": "GtE",
            "Gt": "Lt",
            "GtE": "LtE",
            "In": "ReverseIn",
            "NotIn": "ReverseNotIn",
        }[operator]
    else:
        raise SystemExit("Ambiguous direct security dependency marker")
    return variable.lower(), operator, value


def marker_context(marker: str) -> MarkerContext:
    if not marker.strip():
        return ()
    try:
        if any(
            token.type == tokenize.OP and token.string in {"(", ")"}
            for token in tokenize.generate_tokens(io.StringIO(marker).readline)
        ):
            raise ValueError("Parenthesized security dependency marker")
        expression = parse_marker_expression(marker.strip())
    except (SyntaxError, tokenize.TokenError, ValueError):
        raise SystemExit("Ambiguous direct security dependency marker") from None
    if isinstance(expression, ast.BoolOp):
        if not isinstance(expression.op, ast.And):
            raise SystemExit("Ambiguous direct security dependency marker")
        parts = expression.values
    else:
        parts = [expression]
    return tuple(sorted(marker_clause(part) for part in parts))


def direct_marker_contexts(marker: str) -> tuple[MarkerContext, ...]:
    if not marker.strip():
        return ((),)
    if len(marker) > 1024:
        raise SystemExit("Unbounded direct security dependency marker")
    try:
        expression = parse_marker_expression(marker.strip())
    except (SyntaxError, tokenize.TokenError, ValueError):
        raise SystemExit("Ambiguous direct security dependency marker") from None
    if sum(1 for _ in ast.walk(expression)) > 256:
        raise SystemExit("Unbounded direct security dependency marker")

    def expand(node: ast.expr, depth: int = 0) -> list[MarkerContext]:
        if depth > 32:
            raise SystemExit("Unbounded direct security dependency marker")
        if isinstance(node, ast.BoolOp):
            values: list[MarkerContext]
            if isinstance(node.op, ast.Or):
                values = []
                for child in node.values:
                    values.extend(expand(child, depth + 1))
                    if len(values) > 128:
                        raise SystemExit("Unbounded direct security dependency marker")
            elif isinstance(node.op, ast.And):
                values = [()]
                for child in node.values:
                    current = expand(child, depth + 1)
                    if len(values) * len(current) > 128:
                        raise SystemExit("Unbounded direct security dependency marker")
                    values = [tuple(sorted(set(left + right))) for left in values for right in current]
            else:
                raise SystemExit("Ambiguous direct security dependency marker")
            return values
        context = (marker_clause(node),)
        for option in marker_options(context):
            simple_marker_overlap(option, ())
        return [context]

    expanded = expand(expression)
    if sum(len(marker_options(context)) for context in expanded) > 128:
        raise SystemExit("Unbounded direct security dependency marker")
    unique: list[MarkerContext] = []
    for context in sorted(set(expanded), key=lambda value: (len(value), value)):
        if not marker_overlap(context, ()):
            continue
        if any(not uncovered_marker_fragments(context, [previous]) for previous in unique):
            continue
        unique = [previous for previous in unique if uncovered_marker_fragments(previous, [context])]
        unique.append(context)
    return tuple(unique)


def direct(project: dict[str, Any], *, protected: bool = False) -> tuple[RequirementMap, ContextsByName]:
    if protected:
        uv = project.get("tool", {}).get("uv", {})
        groups = [
            ("uv-constraint", "", uv.get("constraint-dependencies", [])),
            ("uv-build-constraint", "", uv.get("build-constraint-dependencies", [])),
        ]
        groups.extend(
            ("dependency-group", canonical(group), requirements)
            for group, requirements in project.get("dependency-groups", {}).items()
        )
    else:
        groups = [("runtime", "", project["project"].get("dependencies", []))]
        groups.extend(
            ("optional", canonical(group), requirements)
            for group, requirements in project["project"].get("optional-dependencies", {}).items()
        )
    result: RequirementMap = {}
    contexts: ContextsByName = {}
    for scope, group, requirements in groups:
        for requirement in requirements:
            match = re.fullmatch(r"\s*([A-Za-z0-9][A-Za-z0-9_.-]*)(\[[^\]]+\])?\s*(.*)", requirement)
            if match is None:
                raise SystemExit("Ambiguous direct security dependency requirement")
            name = canonical(match.group(1))
            extra = match.group(2)
            requested: tuple[str, ...] = ()
            if extra:
                requested = tuple(sorted(canonical(value.strip()) for value in extra[1:-1].split(",")))
                if any(not re.fullmatch(r"[a-z0-9][a-z0-9-]*", value) for value in requested):
                    raise SystemExit("Ambiguous direct security dependency extras")
            normalized = name + (match.group(2) or "").lower() + re.sub(r"\s+", "", match.group(3)).lower()
            result.setdefault(name, set()).add(normalized)
            for marker in direct_marker_contexts(match.group(3).partition(";")[2]):
                context = (scope, group, requested, marker)
                contexts.setdefault(name, {}).setdefault(context, set()).add(normalized)
    return result, contexts


def versions(lock: dict[str, Any]) -> tuple[RequirementMap, ResolutionsByName]:
    result: RequirementMap = {}
    contexts: ResolutionsByName = {}
    for package in lock["package"]:
        name = canonical(package["name"])
        version = package["version"]
        result.setdefault(name, set()).add(version)
        markers = package.get("resolution-markers")
        domains: list[MarkerContext]
        if markers is None:
            domains = [()]
        else:
            if (
                not isinstance(markers, list)
                or not markers
                or any(not isinstance(marker, str) for marker in cast(list[object], markers))
            ):
                raise SystemExit("Ambiguous locked security dependency resolution marker")
            domains = [marker_context(marker) for marker in cast(list[str], markers)]
        for domain in domains:
            contexts.setdefault(name, {}).setdefault(domain, set()).add(version)
    return result, contexts


def dependency_marker_options(marker: object, extras: tuple[str, ...]) -> list[MarkerContext]:
    if marker is None:
        return [()]
    if not isinstance(marker, str) or not marker.strip() or len(marker) > 1024:
        raise SystemExit("Ambiguous locked security dependency edge marker")
    try:
        expression = parse_marker_expression(marker)
    except (SyntaxError, tokenize.TokenError, ValueError):
        raise SystemExit("Ambiguous locked security dependency edge marker") from None

    selected = extras or ("",)
    if len(selected) > 128:
        raise SystemExit("Unbounded locked security dependency edge extras")
    work = 0

    def options(node: ast.expr, extra: str) -> list[MarkerContext]:
        nonlocal work
        work += 1
        if work > 8192:
            raise SystemExit("Unbounded locked security dependency edge marker")
        if isinstance(node, ast.BoolOp):
            values: list[MarkerContext]
            if isinstance(node.op, ast.Or):
                values = [context for child in node.values for context in options(child, extra)]
            elif isinstance(node.op, ast.And):
                values = [()]
                for child in node.values:
                    current = options(child, extra)
                    if len(values) * len(current) > 128:
                        raise SystemExit("Unbounded locked security dependency edge marker")
                    values = [tuple(sorted(set(left + right))) for left in values for right in current]
            else:
                raise SystemExit("Ambiguous locked security dependency edge marker")
            if len(values) > 128:
                raise SystemExit("Unbounded locked security dependency edge marker")
            return values
        context = (marker_clause(node),)
        variable, operator, value = context[0]
        if variable != "extra":
            return [context]
        normalized = canonical(value)
        if operator in {"Eq", "GtE", "LtE"}:
            accepted = extra == normalized
        elif operator == "NotEq":
            accepted = extra != normalized
        elif operator in {"Gt", "Lt"}:
            accepted = False
        elif operator in {"In", "NotIn", "ReverseIn", "ReverseNotIn"}:
            if len(value) > 256:
                raise SystemExit("Unbounded locked security dependency edge extra")
            if operator in {"ReverseIn", "ReverseNotIn"}:
                accepted = (normalized in extra) == (operator == "ReverseIn")
            else:
                accepted = (extra in normalized) == (operator == "In")
        else:
            raise SystemExit("Ambiguous locked security dependency edge extra")
        return [()] if accepted else []

    result: list[MarkerContext] = []
    seen: set[MarkerContext] = set()
    for extra in selected:
        for context in options(expression, extra):
            if context in seen:
                continue
            seen.add(context)
            result.append(context)
            if len(result) > 128:
                raise SystemExit("Unbounded locked security dependency edge marker")
    return result


def published_reachability(
    lock: dict[str, Any], contexts: ContextsByName
) -> dict[str, set[tuple[str, str, MarkerContext]]]:
    packages: dict[str, list[dict[str, Any]]] = {}
    for item in lock["package"]:
        if not isinstance(item, dict):
            raise SystemExit("Ambiguous locked security dependency identity")
        package = cast(dict[str, Any], item)
        if not isinstance(package.get("name"), str):
            raise SystemExit("Ambiguous locked security dependency identity")
        packages.setdefault(canonical(package["name"]), []).append(package)

    pending: list[tuple[str, tuple[str, ...], str, str, MarkerContext, str | None]] = [
        (name, context[2], context[0], context[1], context[3], None)
        for name, requirements in contexts.items()
        for context in requirements
    ]
    visited: set[tuple[str, tuple[str, ...], str, str, MarkerContext, str | None]] = set()
    reachable: dict[str, set[tuple[str, str, MarkerContext]]] = {}
    while pending:
        if len(pending) > 4096 or len(visited) > 8192:
            raise SystemExit("Unbounded published security dependency graph")
        name, extras, scope, group, context, selected_version = pending.pop()
        state = name, extras, scope, group, context, selected_version
        if state in visited:
            continue
        visited.add(state)
        candidates = packages.get(name, [])
        if not candidates:
            raise SystemExit("Missing locked published security dependency identity for " + name)
        matched = False
        for package in candidates:
            version = package.get("version")
            if not isinstance(version, str):
                raise SystemExit("Ambiguous locked published security dependency version")
            if selected_version is not None and version != selected_version:
                continue
            resolutions = package.get("resolution-markers")
            if resolutions is None:
                domains: list[MarkerContext] = [()]
            elif isinstance(resolutions, list) and resolutions:
                values = cast(list[object], resolutions)
                if not all(isinstance(value, str) for value in values):
                    raise SystemExit("Ambiguous locked published security dependency resolution")
                domains = [marker_context(value) for value in cast(list[str], resolutions)]
            else:
                raise SystemExit("Ambiguous locked published security dependency resolution")
            for domain in domains:
                if not marker_overlap(context, domain):
                    continue
                matched = True
                combined = tuple(sorted(set(context + domain)))
                reachable.setdefault(name, set()).add((scope, group, combined))
                direct_edges = package.get("dependencies", [])
                optional_edges = package.get("optional-dependencies", {})
                if not isinstance(direct_edges, list) or not isinstance(optional_edges, dict):
                    raise SystemExit("Ambiguous locked published security dependency edges")
                groups: dict[str, object] = {}
                for optional, edges in cast(dict[object, object], optional_edges).items():
                    if not isinstance(optional, str):
                        raise SystemExit("Ambiguous locked published security dependency extra")
                    key = canonical(optional)
                    if key in groups:
                        raise SystemExit("Ambiguous locked published security dependency extra")
                    groups[key] = edges
                edges_to_follow: list[object] = list(cast(list[object], direct_edges))
                for extra in extras:
                    requested = groups.get(extra, [])
                    if not isinstance(requested, list):
                        raise SystemExit("Ambiguous locked published security dependency extra")
                    edges_to_follow.extend(cast(list[object], requested))
                for item in edges_to_follow:
                    if not isinstance(item, dict):
                        raise SystemExit("Ambiguous locked published security dependency edge")
                    edge = cast(dict[str, Any], item)
                    if not isinstance(edge.get("name"), str):
                        raise SystemExit("Ambiguous locked published security dependency edge")
                    edge_name = canonical(edge["name"])
                    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", edge_name):
                        raise SystemExit("Ambiguous locked published security dependency edge")
                    requested_extras = edge.get("extra", [])
                    if not isinstance(requested_extras, list) or any(
                        not isinstance(extra, str) for extra in cast(list[object], requested_extras)
                    ):
                        raise SystemExit("Ambiguous locked published security dependency edge extra")
                    normalized_extras = tuple(sorted(canonical(extra) for extra in cast(list[str], requested_extras)))
                    if len(normalized_extras) != len(set(normalized_extras)) or any(
                        not re.fullmatch(r"[a-z0-9][a-z0-9-]*", extra) for extra in normalized_extras
                    ):
                        raise SystemExit("Ambiguous locked published security dependency edge extra")
                    edge_version = edge.get("version")
                    if edge_version is not None and not isinstance(edge_version, str):
                        raise SystemExit("Ambiguous locked published security dependency edge version")
                    for edge_context in dependency_marker_options(edge.get("marker"), extras):
                        next_context = tuple(sorted(set(combined + edge_context)))
                        if not marker_overlap(next_context, ()):
                            continue
                        pending.append((edge_name, normalized_extras, scope, group, next_context, edge_version))
        if not matched and selected_version is not None:
            raise SystemExit("Missing selected locked published security dependency version for " + name)
    return reachable


def requested_extra_reachability(
    lock: dict[str, Any],
    previous: ContextsByName,
    current: ContextsByName,
    requested: list[tuple[str, DependencyContext]],
) -> dict[str, set[tuple[str, str, MarkerContext]]]:
    if len(requested) > 64:
        raise SystemExit("Unbounded newly requested security dependency extras")
    result: dict[str, set[tuple[str, str, MarkerContext]]] = {}
    for root, context in requested:
        selected = published_reachability(lock, {root: {context: current[root][context]}})
        alternatives: ContextRequirements = {}
        for original, requirements in previous.get(root, {}).items():
            if (
                original[:2] != context[:2]
                or not set(original[2]).issubset(context[2])
                or not marker_overlap(original[3], context[3])
            ):
                continue
            shared = tuple(sorted(set(original[3] + context[3])))
            counterfactual = original[0], original[1], original[2], shared
            alternatives.setdefault(counterfactual, set()).update(requirements)
        without = published_reachability(lock, {root: alternatives}) if alternatives else {}
        for name, audiences in selected.items():
            for scope, group, marker in audiences:
                prior = [
                    previous_marker
                    for previous_scope, previous_group, previous_marker in without.get(name, set())
                    if previous_scope == "runtime" or (previous_scope, previous_group) == (scope, group)
                ]
                for uncovered in uncovered_marker_fragments(marker, prior):
                    result.setdefault(name, set()).add((scope, group, uncovered))
    return result


def audience_covers(previous: tuple[str, str, MarkerContext], current: tuple[str, str, MarkerContext]) -> bool:
    if previous[0] != "runtime" and previous[:2] != current[:2]:
        return False
    return not uncovered_marker_fragments(current[2], [previous[2]])


def stable_version(value: str) -> StableRelease:
    match = re.fullmatch(r"(?:(\d+)!)?(\d+(?:\.\d+)*)(?:\.post(\d+))?", value)
    if match is None:
        raise SystemExit("Unsupported direct security dependency minimum")
    release = tuple(int(part) for part in match.group(2).split("."))
    while release and release[-1] == 0:
        release = release[:-1]
    post = -1 if match.group(3) is None else int(match.group(3))
    return int(match.group(1) or 0), release, post


def is_numeric_platform_release(value: str) -> bool:
    if len(value) > 256:
        raise SystemExit("Unbounded platform security dependency marker")
    return (
        re.fullmatch(
            r"v?(?:[0-9]+!)?[0-9]+(?:\.[0-9]+)*"
            r"(?:[._-]?(?:alpha|a|beta|b|preview|pre|c|rc)[._-]?[0-9]*)?"
            r"(?:(?:-[0-9]+)|(?:[._-]?(?:post|rev|r)[._-]?[0-9]*))?"
            r"(?:[._-]?dev[._-]?[0-9]*)?"
            r"(?:\+[a-z0-9]+(?:[._-][a-z0-9]+)*)?"
            r"(?:\.\*)?",
            value.strip(),
            re.IGNORECASE,
        )
        is not None
    )


def numeric_platform_release_candidate(value: str) -> str | None:
    match = re.fullmatch(
        r"v?(?P<release>[0-9]+(?:\.[0-9]+)*)"
        r"(?:[._-]?(?P<stage>alpha|a|beta|b|preview|pre|c|rc)[._-]?(?P<serial>[0-9]*))?"
        r"(?:(?:-(?P<implicit_post>[0-9]+))|"
        r"(?:[._-]?(?P<post>post|rev|r)[._-]?(?P<post_serial>[0-9]*)))?"
        r"(?:[._-]?dev[._-]?(?P<development>[0-9]*))?",
        value.strip(),
        re.IGNORECASE,
    )
    if match is None:
        return None
    result = match.group("release")
    stage = match.group("stage")
    if stage is not None:
        result += {"alpha": "a", "a": "a", "beta": "b", "b": "b"}.get(stage.lower(), "rc")
        result += match.group("serial") or "0"
    if match.group("implicit_post") is not None:
        result += ".post" + match.group("implicit_post")
    elif match.group("post") is not None:
        result += ".post" + (match.group("post_serial") or "0")
    if match.group("development") is not None:
        result += ".dev" + (match.group("development") or "0")
    return result


def marker_version_bounds(
    variable: str, value: str, *, release_width: int = 3
) -> tuple[tuple[int, ...], tuple[int, ...], bool, bool]:
    match = re.fullmatch(
        r"(\d+(?:\.\d+)*)(?:(a|b|rc)(\d+))?(?:\.post(\d+))?(?:\.dev(\d+))?(\.\*)?",
        value.strip() if variable == "platform_release" else value,
    )
    if match is None:
        raise SystemExit("Ambiguous Python security dependency marker")
    components = match.group(1).split(".")
    if len(components) > 32:
        if variable == "platform_release":
            raise SystemExit("Unbounded platform security dependency marker")
        raise SystemExit("Unbounded Python security dependency marker")
    if variable != "platform_release" and len(components) < 2:
        raise SystemExit("Ambiguous Python security dependency marker")
    if any(len(component) > 9 for component in components) or any(
        len(match.group(index)) > 9 for index in (3, 4, 5) if match.group(index) is not None
    ):
        raise SystemExit("Unbounded Python security dependency marker")

    release = tuple(int(component) for component in components)
    release += (0,) * max(0, release_width - len(release))
    prerelease = match.group(2) is not None or match.group(5) is not None
    wildcard = match.group(6) is not None
    if wildcard and (prerelease or match.group(4) is not None):
        raise SystemExit("Ambiguous wildcard security dependency marker")
    if variable == "python_version" and (
        any(component != 0 for component in release[2:]) or prerelease or match.group(4) is not None
    ):
        raise SystemExit("Ambiguous Python security dependency marker")

    phase = (
        -4
        if match.group(5) is not None and match.group(2) is None and match.group(4) is None
        else {"a": -3, "b": -2, "rc": -1}.get(match.group(2) or "", 0)
    )
    serial = int(match.group(3) or 0)
    post = -1 if match.group(4) is None else int(match.group(4))
    development = -1 if match.group(5) is not None else 0
    development_serial = int(match.group(5) or 0)
    if variable == "python_version" or wildcard:
        start = release + (-5, 0, -1, -1, 0)
        prefix = 2 if variable == "python_version" else len(components)
        stop = release[: prefix - 1] + (release[prefix - 1] + 1,) + (0,) * (len(release) - prefix)
        stop += -5, 0, -1, -1, 0
    else:
        start = release + (phase, serial, post, development, development_serial)
        stop = start[:-1] + (development_serial + 1,)
    return start, stop, wildcard, prerelease


def simple_marker_overlap(requirement: MarkerContext, resolution: MarkerContext) -> bool:
    clauses: dict[str, list[MarkerClause]] = {}
    for variable, operator, value in requirement + resolution:
        family = "python" if variable in {"python_version", "python_full_version"} else variable
        clauses.setdefault(family, []).append((variable, operator, value))
    for family, constraints in clauses.items():
        platform_memberships = [
            clause for clause in constraints if family == "platform_release" and clause[1] in {"In", "NotIn"}
        ]
        platform_raw_equalities = [
            clause for clause in constraints if family == "platform_release" and clause[1] == "ArbitraryEq"
        ]
        platform_raw_exclusions = [
            clause for clause in constraints if family == "platform_release" and clause[1] == "ArbitraryNotEq"
        ]
        comparisons = [
            clause
            for clause in constraints
            if family != "platform_release" or clause[1] not in {"In", "NotIn", "ArbitraryEq", "ArbitraryNotEq"}
        ]
        numeric_platform_values = [
            family == "platform_release" and is_numeric_platform_release(value) for _, _, value in comparisons
        ]
        if family == "platform_release" and any(numeric_platform_values) and not all(numeric_platform_values):
            if any(
                not numeric and operator != "NotEq"
                for numeric, (_, operator, _) in zip(numeric_platform_values, comparisons, strict=True)
            ):
                return False
            comparisons = [
                clause for numeric, clause in zip(numeric_platform_values, comparisons, strict=True) if numeric
            ]
            numeric_platform_values = [True] * len(comparisons)
        numeric_platform_release = family == "platform_release" and bool(comparisons) and all(numeric_platform_values)

        def platform_witness_matches(
            candidate: str,
            memberships: list[MarkerClause] = platform_memberships,
            exclusions: list[MarkerClause] = platform_raw_exclusions,
        ) -> bool:
            return all((candidate in value) == (operator == "In") for _, operator, value in memberships) and all(
                candidate.lower() != value.lower() for _, _, value in exclusions
            )

        def anchored_platform_witness() -> str | None:
            for context in (resolution, requirement):
                equalities = [
                    value.strip()
                    for variable, operator, value in context
                    if variable == "platform_release" and operator == "Eq" and not value.rstrip().endswith(".*")
                ]
                if not equalities:
                    continue
                local = [
                    clause
                    for clause in context
                    if clause[0] == "platform_release" and clause[1] in {"In", "NotIn", "ArbitraryNotEq"}
                ]
                for candidate in equalities:
                    if all(
                        (candidate in value) == (operator == "In")
                        if operator in {"In", "NotIn"}
                        else candidate.lower() != value.lower()
                        for _, operator, value in local
                    ):
                        return candidate
                return None
            return None

        if family == "platform_release" and (platform_raw_equalities or platform_raw_exclusions):
            if any(len(value) > 256 for _, _, value in platform_raw_equalities + platform_raw_exclusions):
                raise SystemExit("Unbounded platform security dependency marker")
            if platform_raw_equalities:
                raw_values = {value.lower() for _, _, value in platform_raw_equalities}
                if len(raw_values) != 1:
                    return False
                anchor = (
                    anchored_platform_witness()
                    if any(variable == "platform_release" and operator == "Eq" for variable, operator, _ in resolution)
                    and not any(
                        variable == "platform_release" and operator == "ArbitraryEq"
                        for variable, operator, _ in resolution
                    )
                    else None
                )
                selected = next(
                    (
                        value
                        for variable, operator, value in resolution
                        if variable == "platform_release" and operator == "ArbitraryEq"
                    ),
                    platform_raw_equalities[0][2],
                )
                if anchor is not None:
                    if anchor.lower() not in raw_values:
                        return False
                    selected = anchor
                if not platform_witness_matches(selected):
                    return False
                if not comparisons:
                    continue
                if numeric_platform_release:
                    normalized = numeric_platform_release_candidate(selected)
                    if normalized is None:
                        raise SystemExit("Ambiguous platform security dependency raw equality")
                    selected = normalized
                if not simple_marker_overlap(tuple(comparisons), (("platform_release", "Eq", selected),)):
                    return False
                continue

        if numeric_platform_release and platform_memberships:
            if any(len(value) > 256 for _, _, value in platform_memberships):
                raise SystemExit("Unbounded platform security dependency marker")
            anchor = anchored_platform_witness()
            included = [value for _, operator, value in platform_memberships if operator == "In"]
            if included:
                shortest = min(included, key=len)
                if len(shortest) > 128:
                    raise SystemExit("Unbounded platform security dependency membership")
                candidates = {
                    shortest[start:stop]
                    for start in range(len(shortest) + 1)
                    for stop in range(start, len(shortest) + 1)
                }
                if len(candidates) > 4096:
                    raise SystemExit("Unbounded platform security dependency membership")
                unsupported = False
                matched = False
                for membership_candidate in sorted(candidates):
                    if (
                        anchor is not None
                        and membership_candidate != anchor
                        or not platform_witness_matches(membership_candidate)
                        or not is_numeric_platform_release(membership_candidate)
                    ):
                        continue
                    normalized = numeric_platform_release_candidate(membership_candidate)
                    if normalized is None:
                        unsupported = True
                        continue
                    try:
                        _, _, wildcard, _ = marker_version_bounds("platform_release", normalized)
                    except SystemExit:
                        unsupported = True
                        continue
                    if wildcard:
                        unsupported = True
                        continue
                    if simple_marker_overlap(tuple(comparisons), (("platform_release", "Eq", normalized),)):
                        matched = True
                        break
                if not matched:
                    if unsupported:
                        raise SystemExit("Ambiguous platform security dependency membership")
                    return False
                continue
            if anchor is not None:
                if not platform_witness_matches(anchor):
                    return False
                normalized = numeric_platform_release_candidate(anchor)
                if normalized is None:
                    raise SystemExit("Ambiguous platform security dependency membership")
                if not simple_marker_overlap(tuple(comparisons), (("platform_release", "Eq", normalized),)):
                    return False
                continue
            equalities = [value for _, operator, value in comparisons if operator == "Eq" and not value.endswith(".*")]
            if equalities:
                if not simple_marker_overlap(tuple(comparisons), ()):
                    return False
                matched = False
                for numeric_equality in equalities:
                    normalized = numeric_platform_release_candidate(numeric_equality)
                    if normalized is None:
                        raise SystemExit("Ambiguous platform security dependency membership")
                    match = re.fullmatch(r"(\d+(?:\.\d+)*)(.*)", normalized)
                    if match is None:
                        raise SystemExit("Ambiguous platform security dependency membership")
                    release, suffix = match.groups()
                    components = release.split(".")
                    if len(components) > 32:
                        raise SystemExit("Unbounded platform security dependency membership")
                    for trailing in range(33 - len(components)):
                        for leading in range(10 - len(components[0])):
                            raw_candidate = "0" * leading + release + ".0" * trailing + suffix
                            if len(raw_candidate) > 256 or not platform_witness_matches(raw_candidate):
                                continue
                            if simple_marker_overlap(tuple(comparisons), (("platform_release", "Eq", normalized),)):
                                matched = True
                                break
                        if matched:
                            break
                    if matched:
                        break
                if not matched:
                    raise SystemExit("Ambiguous platform security dependency membership")
                continue
        elif numeric_platform_release and platform_raw_exclusions:
            anchor = anchored_platform_witness()
            if anchor is not None and not platform_witness_matches(anchor):
                return False
        if family in {"python", "implementation_version"} or numeric_platform_release:
            if numeric_platform_release:
                constraints = comparisons
            release_width = max(
                3,
                max(
                    (
                        len(match.group().split("."))
                        for _, _, value in constraints
                        if (match := re.match(r"\d+(?:\.\d+)*", value.strip() if numeric_platform_release else value))
                    ),
                    default=3,
                ),
            )
            lower: tuple[int, ...] = (0,) * release_width + (-5, 0, -1, -1, 0)
            upper: tuple[int, ...] | None = None
            excluded: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
            for variable, operator, value in constraints:
                start, stop, wildcard, prerelease = marker_version_bounds(variable, value, release_width=release_width)
                if wildcard and operator not in {"Eq", "NotEq"}:
                    raise SystemExit("Ambiguous wildcard security dependency marker")
                if operator == "Eq":
                    lower = max(lower, start)
                    upper = stop if upper is None else min(upper, stop)
                elif operator == "NotEq":
                    excluded.append((start, stop))
                elif operator in {"Lt", "RawLt"}:
                    ceiling = start
                    if operator == "Lt" and variable != "python_version" and not prerelease:
                        if start[-3] == -1:
                            ceiling = start[:-5] + (-5, 0, -1, -1, 0)
                        else:
                            ceiling = start[:-2] + (-1, 0)
                    upper = ceiling if upper is None else min(upper, ceiling)
                elif operator in {"LtE", "RawLtE"}:
                    ceiling = stop
                    if operator == "RawLtE" and variable != "python_version" and start[-3] == -1 and start[-2] == 0:
                        if prerelease:
                            ceiling = start[:-4] + (start[-4] + 1, -1, -1, 0)
                        else:
                            ceiling = start[:-6] + (start[-6] + 1, -5, 0, -1, -1, 0)
                    upper = ceiling if upper is None else min(upper, ceiling)
                elif operator in {"Gt", "RawGt"}:
                    floor = stop
                    if operator == "Gt" and variable != "python_version" and start[-3] == -1 and start[-2] == 0:
                        if prerelease:
                            floor = start[:-4] + (start[-4] + 1, -1, -1, 0)
                        else:
                            floor = start[:-6] + (start[-6] + 1, -5, 0, -1, -1, 0)
                    lower = max(lower, floor)
                elif operator in {"GtE", "RawGtE"}:
                    floor = start
                    if operator == "RawGtE" and variable != "python_version" and not prerelease:
                        if start[-3] == -1:
                            floor = start[:-5] + (-5, 0, -1, -1, 0)
                        else:
                            floor = start[:-2] + (-1, 0)
                    lower = max(lower, floor)
                else:
                    raise SystemExit("Ambiguous Python security dependency marker")
            if upper is not None and lower >= upper:
                return False
            candidate = lower
            for start, stop in sorted(excluded):
                if start <= candidate < stop:
                    candidate = stop
            if upper is not None and candidate >= upper:
                return False
        else:
            if family not in {
                "sys_platform",
                "os_name",
                "platform_system",
                "platform_machine",
                "platform_release",
                "platform_version",
                "platform_python_implementation",
                "implementation_name",
                "extra",
            }:
                raise SystemExit("Unsupported security dependency marker variable")
            equality: str | None = None
            memberships: list[str] = []
            required_substrings: list[str] = []
            for _, operator, value in constraints:
                if len(value) > 256:
                    raise SystemExit("Unbounded platform security dependency marker")
                if operator in {"Eq", "GtE", "LtE"}:
                    if equality is not None and equality != value:
                        return False
                    equality = value
                elif operator in {"Gt", "Lt"}:
                    return False
                elif operator == "In":
                    memberships.append(value)
                elif operator == "ReverseIn":
                    required_substrings.append(value)
                elif operator not in {"NotEq", "NotIn", "ReverseNotIn", "ArbitraryNotEq"}:
                    raise SystemExit("Ambiguous platform security dependency marker")

            def matches(platform_candidate: str, terms: list[MarkerClause] = constraints) -> bool:
                for _, operator, value in terms:
                    if (
                        operator in {"Eq", "GtE", "LtE"}
                        and platform_candidate != value
                        or operator == "NotEq"
                        and platform_candidate == value
                        or operator == "ArbitraryNotEq"
                        and platform_candidate.lower() == value.lower()
                        or operator in {"Lt", "Gt"}
                        or operator == "In"
                        and platform_candidate not in value
                        or operator == "NotIn"
                        and platform_candidate in value
                        or operator == "ReverseIn"
                        and value not in platform_candidate
                        or operator == "ReverseNotIn"
                        and value in platform_candidate
                    ):
                        return False
                return True

            if equality is not None:
                if not matches(equality):
                    return False
            elif memberships:
                shortest = min(memberships, key=len)
                if len(shortest) > 128:
                    raise SystemExit("Unbounded platform security dependency membership")
                candidates = {
                    shortest[start:stop]
                    for start in range(len(shortest) + 1)
                    for stop in range(start, len(shortest) + 1)
                }
                if len(candidates) > 4096:
                    raise SystemExit("Unbounded platform security dependency membership")
                if not any(matches(platform_candidate) for platform_candidate in candidates):
                    return False
            else:
                if sum(map(len, required_substrings)) > 4096:
                    raise SystemExit("Unbounded platform security dependency substring")
                if any(
                    forbidden in required
                    for _, operator, forbidden in constraints
                    if operator == "ReverseNotIn"
                    for required in required_substrings
                ) or any(operator == "ReverseNotIn" and not value for _, operator, value in constraints):
                    return False
                platform_candidate = "\x00".join(required_substrings)
                for _ in range(258):
                    if matches(platform_candidate):
                        break
                    platform_candidate += "\x00"
                else:
                    raise SystemExit("Ambiguous platform security dependency marker")
    return True


def marker_options(context: MarkerContext) -> list[MarkerContext]:
    options: list[MarkerContext] = [()]
    allowed_platforms = {
        "sys_platform",
        "os_name",
        "platform_system",
        "platform_machine",
        "platform_release",
        "platform_version",
        "platform_python_implementation",
        "implementation_name",
        "extra",
    }
    for variable, operator, value in context:
        if operator in {"ReverseIn", "ReverseNotIn"}:
            if variable not in allowed_platforms or variable == "platform_release":
                raise SystemExit("Unsupported reversed security dependency membership marker")
            if len(value) > 256 or value and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value) is None:
                raise SystemExit("Ambiguous reversed security dependency membership marker")
            options = [option + ((variable, operator, value),) for option in options]
            continue
        if operator == "Compatible":
            if variable not in {"python_version", "python_full_version", "implementation_version", "platform_release"}:
                raise SystemExit("Unsupported compatible security dependency marker")
            compatible = re.fullmatch(
                r"(\d+(?:\.\d+)+)"
                r"((?:(?:a|b|rc)\d+)?(?:\.post\d+)?(?:\.dev\d+)?)",
                value,
            )
            if compatible is None:
                raise SystemExit("Ambiguous compatible security dependency marker")
            components = compatible.group(1).split(".")
            if len(components) > 32 or any(len(component) > 9 for component in components):
                raise SystemExit("Ambiguous compatible security dependency marker")
            ceiling = [int(component) for component in components[:-1]]
            ceiling[-1] += 1
            if len(ceiling) == 1:
                ceiling.append(0)
            upper = ".".join(str(component) for component in ceiling)
            if variable == "python_version":
                minor = int(components[1])
                lower = f"{int(components[0])}.{minor}"
                width = max(3, len(components))
                projected = marker_version_bounds("platform_release", lower, release_width=width)[0]
                actual = marker_version_bounds("platform_release", value, release_width=width)[0]
                if projected < actual:
                    lower = f"{int(components[0])}.{minor + 1}"
                if len(ceiling) > 2 and any(component != 0 for component in ceiling[2:]):
                    upper = f"{ceiling[0]}.{ceiling[1] + 1}"
                else:
                    upper = f"{ceiling[0]}.{ceiling[1]}"
                value = lower
            options = [option + ((variable, "GtE", value), (variable, "Lt", upper)) for option in options]
            continue
        if operator == "ArbitraryEq":
            if variable == "python_version":
                pattern = r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
            elif variable in {"python_full_version", "implementation_version"}:
                pattern = (
                    r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
                    r"(?:(?:a|b|rc)(?:0|[1-9]\d*))?(?:\.post(?:0|[1-9]\d*))?(?:\.dev(?:0|[1-9]\d*))?"
                )
            elif variable == "platform_release":
                if len(value) > 256 or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.!+-]*", value.strip()) is None:
                    raise SystemExit("Ambiguous platform security dependency raw equality")
                options = [option + ((variable, operator, value.strip()),) for option in options]
                continue
            else:
                raise SystemExit("Unsupported arbitrary security dependency marker variable")
            if re.fullmatch(pattern, value) is None:
                return []
            operator = "Eq"
        if operator not in {"In", "NotIn"}:
            options = [option + ((variable, operator, value),) for option in options]
            continue
        if variable == "python_version":
            pattern = r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:\.0)?"
        elif variable in {"python_full_version", "implementation_version"}:
            pattern = (
                r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
                r"(?:(?:a|b|rc)(?:0|[1-9]\d*))?(?:\.post(?:0|[1-9]\d*))?(?:\.dev(?:0|[1-9]\d*))?"
            )
        elif variable in allowed_platforms:
            pattern = r"[A-Za-z0-9][A-Za-z0-9_.-]*"
        else:
            raise SystemExit("Unsupported security dependency membership marker variable")
        if variable not in allowed_platforms and len(value) > 128:
            raise SystemExit("Unbounded Python security dependency membership marker")
        values = tuple(item.strip() for item in value.split(","))
        if (
            not values
            or len(values) > 16
            or len(set(values)) != len(values)
            or any(
                not re.fullmatch(pattern, item)
                if variable in allowed_platforms
                else not any(
                    re.fullmatch(pattern, item[start:stop])
                    for start in range(len(item))
                    for stop in range(start + 1, len(item) + 1)
                )
                for item in values
            )
        ):
            raise SystemExit("Ambiguous security dependency membership marker")
        if variable in allowed_platforms:
            options = [option + ((variable, operator, value),) for option in options]
        else:
            members = tuple(
                sorted(
                    {
                        value[start:stop]
                        for start in range(len(value))
                        for stop in range(start + 1, len(value) + 1)
                        if re.fullmatch(pattern, value[start:stop])
                    }
                )
            )
            if len(members) > 64:
                raise SystemExit("Unbounded Python security dependency membership marker")
            if operator == "In":
                options = [option + ((variable, "Eq", member),) for option in options for member in members]
            else:
                exclusions = tuple((variable, "NotEq", member) for member in members)
                options = [option + exclusions for option in options]
        if len(options) > 64:
            raise SystemExit("Ambiguous security dependency membership marker")
    return options


def marker_overlap(requirement: MarkerContext, resolution: MarkerContext) -> bool:
    requirements, resolutions = marker_options(requirement), marker_options(resolution)
    if len(requirements) * len(resolutions) > 128:
        raise SystemExit("Ambiguous security dependency membership marker")
    return any(simple_marker_overlap(left, right) for left in requirements for right in resolutions)


def uncovered_marker_fragments(
    domain: MarkerContext, coverings: list[MarkerContext], *, anchor_platform_release: bool = False
) -> tuple[MarkerContext, ...]:
    platform_equalities = [
        value.strip()
        for variable, operator, value in domain
        if variable == "platform_release" and operator == "Eq" and not value.rstrip().endswith(".*")
    ]
    raw_coverings = [
        covering
        for covering in coverings
        if any(
            variable == "platform_release" and operator in {"In", "NotIn", "ArbitraryEq"}
            for variable, operator, _ in covering
        )
    ]
    if (
        anchor_platform_release
        and len(platform_equalities) == 1
        and raw_coverings
        and not any(
            variable == "platform_release" and operator in {"In", "NotIn", "ArbitraryEq", "ArbitraryNotEq"}
            for variable, operator, _ in domain
        )
    ):
        domain = tuple(sorted(domain + (("platform_release", "ArbitraryEq", platform_equalities[0]),)))
    opposite = {
        "Eq": "NotEq",
        "NotEq": "Eq",
        "Lt": "GtE",
        "LtE": "Gt",
        "Gt": "LtE",
        "GtE": "Lt",
        "RawLt": "GtE",
        "RawLtE": "Gt",
        "RawGt": "LtE",
        "RawGtE": "Lt",
        "In": "NotIn",
        "NotIn": "In",
        "ReverseIn": "ReverseNotIn",
        "ReverseNotIn": "ReverseIn",
        "ArbitraryEq": "ArbitraryNotEq",
        "ArbitraryNotEq": "ArbitraryEq",
    }
    fragments = {tuple(sorted(set(option))) for option in marker_options(domain) if simple_marker_overlap(option, ())}
    work = 0
    for covering in coverings:
        options = marker_options(covering)
        if len(fragments) * len(options) > 128:
            raise SystemExit("Ambiguous security dependency marker partition")
        for option in options:
            remaining: set[MarkerContext] = set()
            for fragment in fragments:
                work += 1
                if work > 2048:
                    raise SystemExit("Ambiguous security dependency marker partition")
                if not simple_marker_overlap(option, fragment):
                    remaining.add(fragment)
                    continue
                prefix = fragment
                for variable, operator, value in option:
                    if operator not in opposite:
                        raise SystemExit("Ambiguous security dependency marker partition")
                    inverse = opposite[operator]
                    if variable in {"python_full_version", "implementation_version"} or (
                        variable == "platform_release" and is_numeric_platform_release(value)
                    ):
                        if operator == "GtE":
                            inverse = "RawLt"
                        elif operator == "Gt":
                            inverse = "RawLtE"
                        elif operator == "Lt":
                            inverse = "RawGtE"
                        elif operator == "LtE":
                            inverse = "RawGt"
                    elif variable != "python_version" and operator in {"GtE", "LtE"}:
                        inverse = "NotEq"
                    excluded = tuple(sorted(set(prefix + ((variable, inverse, value),))))
                    if simple_marker_overlap(excluded, ()):
                        remaining.add(excluded)
                    prefix = tuple(sorted(set(prefix + ((variable, operator, value),))))
                    if len(remaining) > 128 or len(prefix) > 128:
                        raise SystemExit("Ambiguous security dependency marker partition")
            fragments = remaining
            if not fragments:
                break
    return tuple(sorted(fragments))


def reconcile_resolution_domains(
    previous: ResolutionDomains, current: ResolutionDomains
) -> tuple[ResolutionDomains, ResolutionDomains]:
    if previous == current:
        return previous, current
    domains = sorted(previous.keys() | current.keys())
    if len(domains) > 128:
        raise SystemExit("Unbounded security dependency resolution-domain refinement")
    explicit_prerelease = any(
        variable in {"python_full_version", "implementation_version", "platform_release"}
        and re.search(r"\d+\.\d+(?:\.\d+)?(?:a|b|rc)\d+", value) is not None
        for domain in domains
        for variable, _, value in domain
    )
    fragments: set[MarkerContext] = set()
    work = 0
    for domain in domains:
        for option in marker_options(domain):
            candidate = tuple(sorted(set(option)))
            if not simple_marker_overlap(candidate, ()):
                raise SystemExit("Ambiguous security dependency resolution-domain refinement")
            remaining: set[MarkerContext] = {candidate}
            refined: set[MarkerContext] = set()
            for fragment in fragments:
                work += 1
                if work > 4096:
                    raise SystemExit("Unbounded security dependency resolution-domain refinement")
                if not simple_marker_overlap(fragment, candidate):
                    refined.add(fragment)
                    continue
                intersection = tuple(sorted(set(fragment + candidate)))
                refined.add(intersection)
                refined.update(uncovered_marker_fragments(fragment, [candidate]))
                remaining = {
                    uncovered for value in remaining for uncovered in uncovered_marker_fragments(value, [fragment])
                }
                if len(refined) + len(remaining) > 128:
                    raise SystemExit("Unbounded security dependency resolution-domain refinement")
            refined.update(remaining)
            if len(refined) > 128:
                raise SystemExit("Unbounded security dependency resolution-domain refinement")
            fragments = refined
    aligned_previous: ResolutionDomains = {}
    aligned_current: ResolutionDomains = {}
    for fragment in fragments:
        old = {
            release for domain, releases in previous.items() if marker_overlap(domain, fragment) for release in releases
        }
        new = {
            release for domain, releases in current.items() if marker_overlap(domain, fragment) for release in releases
        }
        if bool(old) != bool(new):
            if not explicit_prerelease:
                earliest = {
                    (variable, marker_version_bounds(variable, value)[0][:-5])
                    for variable, operator, value in fragment
                    if operator == "RawGtE"
                }
                final = {
                    (variable, marker_version_bounds(variable, value)[0][:-5])
                    for variable, operator, value in fragment
                    if operator == "RawLt"
                }
                if earliest & final:
                    continue
            raise SystemExit("Do not remove or widen a locked security dependency resolution domain")
        if old:
            aligned_previous[fragment] = old
            aligned_current[fragment] = new
    return aligned_previous, aligned_current


def minimums(requirements: set[str], *, allow_missing: bool = False, exact: bool = False) -> list[StableRelease]:
    result: list[StableRelease] = []
    for requirement in requirements:
        specifier = requirement.split(";", 1)[0]
        pattern = r"(?<![<>=!~])(?:===|>=|>|==|~=)([^,;]+)" if exact else r"(?<![<>=!~])(?:>=|>|~=)([^,;]+)"
        matches = re.findall(pattern, specifier)
        if exact:
            matches = [value.strip().removesuffix(".*") for value in matches]
        else:
            matches.extend(re.findall(r"(?<![<>=!~])==\s*((?:(?:\d+)!)?\d+(?:\.\d+)*)\.\*(?=\s*(?:,|$))", specifier))
        if not matches:
            if allow_missing:
                continue
            raise SystemExit("Missing or ambiguous direct security dependency minimum")
        bounds = published_bounds(requirement)
        lower = [bound for bound in bounds if bound[0] in {">=", ">"}]
        pinned = [bound for bound in bounds if bound[0] in {"==", "==="}]
        for _, epoch, components, post, _ in pinned:
            if not allows_published_release(bounds, (epoch, components, post)):
                raise SystemExit("Missing or ambiguous direct security dependency minimum")
        for operator, epoch, components, post, _ in lower:
            release = epoch, components, post
            for upper_operator, upper_epoch, upper_components, upper_post, _ in bounds:
                if upper_operator not in {"<", "<="}:
                    continue
                upper = upper_epoch, upper_components, upper_post
                if (
                    release > upper
                    or release == upper
                    and (operator == ">" or upper_operator == "<")
                    or operator == ">"
                    and post == -1
                    and upper_epoch == epoch
                    and upper_components == components
                ):
                    raise SystemExit("Missing or ambiguous direct security dependency minimum")
        floors = lower + pinned if exact else lower
        if not floors:
            raise SystemExit("Missing or ambiguous direct security dependency minimum")
        result.append(max((epoch, components, post) for _, epoch, components, post, _ in floors))
    return sorted(result)


def matches_protected_release(requirements: set[str], release: StableRelease, *, upper_only: bool = False) -> bool:
    for requirement in requirements:
        expression = requirement.split(";", 1)[0]
        match = re.fullmatch(r"\s*([A-Za-z0-9][A-Za-z0-9_.-]*)(\[[^\]]+\])?\s*(.*)", expression)
        if match is None:
            raise SystemExit("Ambiguous protected security dependency requirement")
        if not match.group(3).strip():
            return True
        bounds = published_bounds(requirement)
        if upper_only:
            bounds = tuple(bound for bound in bounds if bound[0] not in {">=", ">"})
        if allows_published_release(bounds, release):
            return True
    return False


def unchanged_nonfloor_bounds(requirement: str) -> tuple[PublishedBound, ...]:
    return tuple(sorted(bound for bound in published_bounds(requirement) if bound[0] not in {">=", ">", "==", "==="}))


def replacement_contexts(
    previous_context: DependencyContext,
    previous_requirements: set[str],
    current_contexts: ContextRequirements,
    domains: ResolutionDomains,
    *,
    exact: bool = False,
) -> ContextRequirements:
    current = current_contexts.get(previous_context, set())
    if len(current) >= len(previous_requirements):
        return {previous_context: current}
    if current or len(previous_requirements) != 1:
        return {}
    original = next(iter(previous_requirements))
    original_minimums = minimums(previous_requirements, allow_missing=True, exact=exact)
    if len(original_minimums) != 1:
        return {}
    replacements = {
        context: requirements
        for context, requirements in current_contexts.items()
        if context[:3] == previous_context[:3] and context[3] and marker_overlap(previous_context[3], context[3])
    }
    if len(replacements) < 2:
        return {}
    for context, requirements in replacements.items():
        if len(requirements) != 1 or uncovered_marker_fragments(context[3], [previous_context[3]]):
            return {}
        replacement = next(iter(requirements))
        if unchanged_nonfloor_bounds(replacement) != unchanged_nonfloor_bounds(original):
            return {}
        replacement_minimums = minimums(requirements, exact=exact)
        if len(replacement_minimums) != 1 or replacement_minimums[0] < original_minimums[0]:
            return {}
    relevant = {
        domain
        for domain, versions in domains.items()
        if marker_overlap(previous_context[3], domain)
        and any(matches_protected_release(previous_requirements, stable_version(version)) for version in versions)
    }
    if len(relevant) < 2:
        return {}
    covered: set[DependencyContext] = set()
    for domain in relevant:
        original_domain = tuple(sorted(set(previous_context[3] + domain)))
        matched = [context for context in replacements if marker_overlap(context[3], original_domain)]
        if not matched or uncovered_marker_fragments(original_domain, [context[3] for context in matched]):
            return {}
        if any(
            replacements[first] != replacements[second]
            and marker_overlap(tuple(sorted(set(first[3] + second[3]))), original_domain)
            for index, first in enumerate(matched)
            for second in matched[index + 1 :]
        ):
            return {}
        covered.update(matched)
    return replacements if covered == set(replacements) else {}


def preserves_requirement_source_markers(
    previous_contexts: ContextRequirements,
    current_contexts: ContextRequirements,
    domains: ResolutionDomains,
    current_domains: ResolutionDomains,
    *,
    extra_review: bool = False,
) -> tuple[bool, bool]:
    previous_sources: dict[RequirementSource, list[MarkerContext]] = {}
    current_sources: dict[RequirementSource, list[MarkerContext]] = {}
    for context, requirements in previous_contexts.items():
        for requirement in requirements:
            previous_sources.setdefault((*context[:3], requirement), []).append(context[3])
    for context, requirements in current_contexts.items():
        for requirement in requirements:
            current_sources.setdefault((*context[:3], requirement), []).append(context[3])
    previous = list(previous_sources.items())
    current = list(current_sources.items())
    if len(previous) > 64 or len(current) > 64 or len(previous) * len(current) > 2048:
        raise SystemExit("Unbounded security dependency source marker assignment")

    def source_bounds(requirement: str) -> tuple[PublishedBound, ...]:
        expression = requirement.split(";", 1)[0]
        match = re.fullmatch(r"\s*([A-Za-z0-9][A-Za-z0-9_.-]*)(\[[^\]]+\])?\s*(.*)", expression)
        if match is None:
            raise SystemExit("Ambiguous security dependency source requirement")
        return published_bounds(requirement) if match.group(3).strip() else ()

    def source_floor(requirement: str) -> StableRelease | None:
        floors = [
            (epoch, release, post)
            for operator, epoch, release, post, _ in source_bounds(requirement)
            if operator in {">=", ">", "==", "==="}
        ]
        return max(floors, default=None)

    def compatible(original: str, replacement: str) -> bool:
        if original == replacement:
            return True
        before, after = source_floor(original), source_floor(replacement)
        if before is not None and (after is None or after < before):
            return False
        original_bounds = source_bounds(original)
        replacement_bounds = source_bounds(replacement)
        if any(bound[0] == "===" for bound in replacement_bounds) and not any(
            bound[0] == "===" for bound in original_bounds
        ):
            return False
        return all(
            preserves_published_security_bound(bound, replacement_bounds)
            for bound in original_bounds
            if bound[0] not in {">=", ">", "==", "==="}
        )

    edges: dict[int, list[int]] = {}
    for index, (identity, markers) in enumerate(previous):
        matching: list[int] = []
        for candidate, (updated, updated_markers) in enumerate(current):
            if updated[:3] != identity[:3] or not compatible(identity[3], updated[3]):
                continue
            if any(uncovered_marker_fragments(marker, updated_markers) for marker in markers):
                continue
            if any(uncovered_marker_fragments(marker, markers) for marker in updated_markers):
                continue
            matching.append(candidate)
        if matching:
            edges[index] = matching

    assigned: dict[int, int] = {}

    def claim(index: int, visited: set[int]) -> bool:
        for candidate in edges[index]:
            if candidate in visited:
                continue
            visited.add(candidate)
            original = assigned.get(candidate)
            if original is None or claim(original, visited):
                assigned[candidate] = index
                return True
        return False

    for index in sorted(edges, key=lambda value: len(edges[value])):
        if not claim(index, set()):
            return False, False

    partitioned = False
    for index, (identity, markers) in enumerate(previous):
        if index in assigned.values():
            continue
        original = identity[3]
        if source_floor(original) is None:
            return False, False
        candidates = [
            (candidate, updated_markers)
            for candidate, (updated, updated_markers) in enumerate(current)
            if candidate not in assigned
            and updated[:3] == identity[:3]
            and compatible(original, updated[3])
            and all(not uncovered_marker_fragments(marker, markers) for marker in updated_markers)
        ]
        if len(candidates) < 2:
            return False, False
        regions = {
            tuple(sorted(set(marker + domain)))
            for marker in markers
            for domain, releases in domains.items()
            if marker_overlap(marker, domain)
            and any(matches_protected_release({original}, stable_version(release)) for release in releases)
        }
        if not regions:
            return False, False
        covered: set[int] = set()
        for region in regions:
            applicable = [
                (candidate, marker)
                for candidate, updated_markers in candidates
                for marker in updated_markers
                if marker_overlap(marker, region)
            ]
            if not applicable or uncovered_marker_fragments(region, [marker for _, marker in applicable]):
                return False, False
            if any(
                first != second and marker_overlap(tuple(sorted(set(left + right))), region)
                for position, (first, left) in enumerate(applicable)
                for second, right in applicable[position + 1 :]
            ):
                return False, False
            covered.update(candidate for candidate, _ in applicable)
        if covered != {candidate for candidate, _ in candidates}:
            return False, False
        for candidate, _ in candidates:
            assigned[candidate] = index
        partitioned = True
    for candidate, (identity, markers) in enumerate(current):
        if candidate in assigned:
            continue
        if identity[0] in {"runtime", "optional"} and identity[2]:
            added_bounds = source_bounds(identity[3])
            for bound in added_bounds:
                reviewed_markers = [
                    marker
                    for original, original_markers in previous
                    if (original[0] == "runtime" or original[:2] == identity[:2])
                    and set(original[2]).issubset(identity[2])
                    and preserves_published_security_bound(bound, source_bounds(original[3]))
                    for marker in original_markers
                ]
                if any(uncovered_marker_fragments(marker, reviewed_markers) for marker in markers):
                    return False, False
            continue
        floor = source_floor(identity[3])
        if floor is None:
            return False, False
        bounds = source_bounds(identity[3])
        reviewed = False
        for domain in domains.keys() | current_domains.keys():
            previous_versions = domains.get(domain, set())
            updated_versions = current_domains.get(domain, set())
            if previous_versions == updated_versions or not any(marker_overlap(marker, domain) for marker in markers):
                continue
            removed = sorted(stable_version(version) for version in previous_versions - updated_versions)
            patched = sorted(stable_version(version) for version in updated_versions - previous_versions)
            if not removed or len(removed) != len(patched):
                continue
            if any(
                updated > previous
                and floor >= updated
                and allows_published_release(bounds, updated)
                and not allows_published_release(bounds, previous)
                for previous, updated in zip(removed, patched, strict=True)
            ):
                reviewed = True
                break
        if not reviewed and extra_review:
            reviewed = any(
                any(marker_overlap(marker, domain) for marker in markers)
                and any(
                    floor >= stable_version(version) and allows_published_release(bounds, stable_version(version))
                    for version in releases
                )
                for domain, releases in current_domains.items()
            )
        if not reviewed:
            return False, False
    return True, partitioned


def preserves_supported_security_branches(
    previous_domains: ResolutionDomains,
    current_domains: ResolutionDomains,
    previous_contexts: ContextRequirements,
    current_contexts: ContextRequirements,
) -> bool:
    observed = False
    for domain in previous_domains.keys() | current_domains.keys():
        previous_versions = previous_domains.get(domain, set())
        current_versions = current_domains.get(domain, set())
        if previous_versions == current_versions:
            continue
        removed = sorted(stable_version(version) for version in previous_versions - current_versions)
        introduced = sorted(stable_version(version) for version in current_versions - previous_versions)
        unchanged = {stable_version(version) for version in previous_versions & current_versions}
        if not removed or len(removed) != len(introduced):
            return False
        validated: dict[StableRelease, DependencyContext] = {}
        for previous_release, patched_release in zip(removed, introduced, strict=True):
            if (
                patched_release <= previous_release
                or patched_release[0] != previous_release[0]
                or not patched_release[1]
                or not previous_release[1]
                or patched_release[1][0] != previous_release[1][0]
            ):
                return False
            for context, previous_requirements in previous_contexts.items():
                requirements = current_contexts.get(context, set())
                if (
                    context in validated.values()
                    or len(previous_requirements) != 1
                    or len(requirements) != 1
                    or not marker_overlap(context[3], domain)
                ):
                    continue
                original = next(iter(previous_requirements))
                replacement = next(iter(requirements))
                bounds = unchanged_nonfloor_bounds(original)
                if (
                    not any(bound[0] in {"<", "<="} for bound in bounds)
                    or unchanged_nonfloor_bounds(replacement) != bounds
                    or not matches_protected_release(previous_requirements, previous_release)
                    or not matches_protected_release(requirements, patched_release)
                ):
                    continue
                before = minimums(previous_requirements, allow_missing=True, exact=True)
                after = minimums(requirements, exact=True)
                if len(before) == 1 and len(after) == 1 and after[0] >= patched_release and after[0] > before[0]:
                    validated[patched_release] = context
                    break
            if patched_release not in validated:
                return False
        for patched_release, context in validated.items():
            candidates = [
                (release, other)
                for release, other in validated.items()
                if release != patched_release and other != context
            ]
            candidates.extend(
                (release, other)
                for release in unchanged
                for other, protected in previous_contexts.items()
                if other != context
                and marker_overlap(other[3], domain)
                and other in current_contexts
                and matches_protected_release(protected, release)
                and matches_protected_release(current_contexts[other], release)
            )
            if not any(
                not matches_protected_release(previous_contexts[context], release)
                and matches_protected_release(current_contexts[other], release)
                for release, other in candidates
            ):
                return False
        observed = True
    return observed


def published_bounds(requirement: str) -> tuple[PublishedBound, ...]:
    expression = requirement.split(";", 1)[0]
    match = re.fullmatch(r"\s*([A-Za-z0-9][A-Za-z0-9_.-]*)(\[[^\]]+\])?\s*(.*)", expression)
    if match is None:
        raise SystemExit("Ambiguous published security dependency requirement")
    name = canonical(match.group(1))
    clauses = match.group(3).split(",")
    if len(clauses) > 256:
        raise SystemExit("Unbounded published security dependency exclusions")
    result: list[PublishedBound] = []
    for clause in clauses:
        match = re.fullmatch(
            r"(===|~=|>=|<=|==|!=|>|<)\s*((?:(\d+)!)?(\d+(?:\.\d+)*)(?:\.post(\d+))?)(\.\*)?",
            clause.strip(),
        )
        if match is None or len(match.group(2)) > 128:
            raise SystemExit("Ambiguous published security dependency bound")
        components = match.group(4).split(".")
        if len(components) > 16 or any(len(component) > 9 for component in components):
            raise SystemExit("Unbounded published security dependency release")
        wildcard = match.group(6) is not None
        if wildcard and (match.group(1) not in {"!=", "=="} or match.group(5) is not None):
            raise SystemExit("Ambiguous published security dependency wildcard")
        epoch, release, post = stable_version(match.group(2))
        if match.group(1) == "===" and any(
            stable_version(version) == (epoch, release, post) and version != match.group(2)
            for version in old_versions.get(name, set()) | new_versions.get(name, set())
        ):
            raise SystemExit("Arbitrary-equality security dependency pin does not match its raw locked release")
        prefix = tuple(int(component) for component in components)
        if match.group(1) == "==" and wildcard:
            ceiling = prefix[:-1] + (prefix[-1] + 1,)
            upper = stable_version(str(epoch) + "!" + ".".join(str(part) for part in ceiling))
            result.extend(((">=", epoch, release, post, False), ("<", upper[0], upper[1], upper[2], False)))
        elif match.group(1) == "~=":
            if len(prefix) < 2 or wildcard:
                raise SystemExit("Ambiguous compatible published security dependency bound")
            ceiling = prefix[:-2] + (prefix[-2] + 1,)
            upper = stable_version(str(epoch) + "!" + ".".join(str(part) for part in ceiling))
            result.extend(((">=", epoch, release, post, False), ("<", upper[0], upper[1], upper[2], False)))
        else:
            result.append((match.group(1), epoch, prefix if wildcard else release, post, wildcard))
    if len(set(result)) != len(result):
        raise SystemExit("Ambiguous duplicate published security dependency bound")
    return tuple(result)


def allows_published_release(bounds: tuple[PublishedBound, ...], release: StableRelease) -> bool:
    for operator, epoch, components, post, wildcard in bounds:
        if wildcard:
            candidate = release[1] + (0,) * max(0, len(components) - len(release[1]))
            if release[0] == epoch and candidate[: len(components)] == components:
                return False
            continue
        bound = epoch, components, post
        if (
            operator == ">="
            and release < bound
            or operator == ">"
            and (release <= bound or post < 0 and release[0] == epoch and release[1] == components and release[2] >= 0)
            or operator == "<="
            and release > bound
            or operator == "<"
            and release >= bound
            or operator in {"==", "==="}
            and release != bound
            or operator == "!="
            and release == bound
        ):
            return False
    return True


def preserves_published_security_bound(previous: PublishedBound, current: tuple[PublishedBound, ...]) -> bool:
    operator, epoch, components, post, wildcard = previous
    if operator in {">", ">="}:
        limit = epoch, components, post
        for updated, candidate_epoch, candidate, candidate_post, candidate_wildcard in current:
            if candidate_wildcard or updated not in {">", ">=", "==", "==="}:
                continue
            bound = candidate_epoch, candidate, candidate_post
            if (
                operator == ">"
                and post < 0
                and candidate_epoch == epoch
                and candidate == components
                and candidate_post >= 0
            ):
                continue
            if bound > limit or bound == limit and (operator == ">=" or updated == ">"):
                return True
        return False
    if operator in {"<", "<="}:
        limit = epoch, components, post
        for updated, candidate_epoch, candidate, candidate_post, candidate_wildcard in current:
            if candidate_wildcard or updated not in {"<", "<=", "==", "==="}:
                continue
            bound = candidate_epoch, candidate, candidate_post
            if bound < limit or bound == limit and (operator == "<=" or updated == "<"):
                return True
        return False
    if operator in {"==", "==="}:
        return any(bound == previous for bound in current)
    if operator != "!=":
        return True
    if not wildcard:
        return not allows_published_release(current, (epoch, components, post))

    start_text = str(epoch) + "!" + ".".join(str(part) for part in components)
    start = stable_version(start_text)
    next_components = components[:-1] + (components[-1] + 1,)
    stop = stable_version(str(epoch) + "!" + ".".join(str(part) for part in next_components))
    for updated, candidate_epoch, candidate, candidate_post, candidate_wildcard in current:
        if (
            updated == "!="
            and candidate_wildcard
            and candidate_epoch == epoch
            and len(candidate) <= len(components)
            and components[: len(candidate)] == candidate
        ):
            return True
        if candidate_wildcard:
            continue
        bound = candidate_epoch, candidate, candidate_post
        if updated in {"<", "<="} and (bound < start or bound == start and updated == "<"):
            return True
        if updated in {">=", ">"} and bound >= stop:
            return True
        if updated in {"==", "==="}:
            padded = candidate + (0,) * max(0, len(components) - len(candidate))
            if candidate_epoch != epoch or padded[: len(components)] != components:
                return True
    return False


def preserves_exact_pinned_release(
    previous: PublishedBound,
    current: tuple[PublishedBound, ...],
    context: MarkerContext,
    previous_domains: ResolutionDomains,
    current_domains: ResolutionDomains,
) -> bool:
    if preserves_published_security_bound(previous, current):
        return True
    operator, epoch, components, post, wildcard = previous
    if operator not in {"==", "==="} or wildcard:
        return False
    pinned = epoch, components, post
    replacements: list[StableRelease] = []
    for domain, versions in previous_domains.items():
        if not marker_overlap(context, domain):
            continue
        prior = {stable_version(version) for version in versions}
        if pinned not in prior:
            continue
        updated = {stable_version(version) for version in current_domains.get(domain, set())}
        removed = prior - updated
        introduced = updated - prior
        if removed != {pinned} or len(introduced) != 1:
            return False
        patched = next(iter(introduced))
        if patched <= pinned:
            return False
        replacements.append(patched)
    if len(set(replacements)) != 1:
        return False
    patched = replacements[0]
    return any(
        candidate_operator == operator and not candidate_wildcard and (epoch, components, post) == patched
        for candidate_operator, epoch, components, post, candidate_wildcard in current
    )


def preserves_dependency_security_bounds(
    previous_contexts: ContextRequirements,
    replacements: ContextReplacements,
    previous_domains: ResolutionDomains,
    domains: ResolutionDomains,
) -> bool:
    for previous_context, previous_requirements in previous_contexts.items():
        for requirement in previous_requirements:
            expression = requirement.split(";", 1)[0]
            match = re.fullmatch(r"\s*([A-Za-z0-9][A-Za-z0-9_.-]*)(\[[^\]]+\])?\s*(.*)", expression)
            if match is None:
                raise SystemExit("Ambiguous unchanged published security dependency requirement")
            clauses = match.group(3).split(",")
            if not any(re.match(r"(?:===|~=|!=|<=|<|>=|>|==)", clause.strip()) for clause in clauses):
                continue
            before = published_bounds(requirement)
            protected = tuple(bound for bound in before if bound[0] in {"<", "<=", "!=", ">", ">=", "==", "==="})
            preserve_releases = any(bound[0] in {"<", "<=", "!=", "==", "==="} for bound in protected)
            context_replacements = replacements.get(previous_context, {})
            if not context_replacements:
                return False
            for replacement_context, candidates in context_replacements.items():
                retained = {
                    stable_version(version)
                    for domain, versions in domains.items()
                    if marker_overlap(replacement_context[3], domain)
                    for version in versions
                    if allows_published_release(before, stable_version(version))
                }
                preserved = False
                for candidate in candidates:
                    after = published_bounds(candidate)
                    if all(
                        preserves_exact_pinned_release(bound, after, replacement_context[3], previous_domains, domains)
                        if bound[0] in {"==", "==="}
                        else preserves_published_security_bound(bound, after)
                        for bound in protected
                    ) and (
                        not preserve_releases or all(allows_published_release(after, release) for release in retained)
                    ):
                        preserved = True
                        break
                if not preserved:
                    return False
    return True


def published_lower_bound_excludes(bounds: tuple[PublishedBound, ...], epoch: int, prefix: tuple[int, ...]) -> bool:
    for operator, bound_epoch, components, _post, wildcard in bounds:
        if wildcard or operator not in {">=", ">"}:
            continue
        if epoch < bound_epoch:
            return True
        if epoch > bound_epoch:
            continue
        boundary = components + (0,) * max(0, len(prefix) - len(components))
        if prefix < boundary[: len(prefix)]:
            return True
    return False


def excludes_affected_published_branch(
    previous_bounds: tuple[PublishedBound, ...],
    current_bounds: tuple[PublishedBound, ...],
    removed: StableRelease,
    patched: StableRelease,
    preserved: set[StableRelease],
) -> bool:
    if (
        removed[0] != patched[0]
        or not removed[1]
        or not patched[1]
        or removed[1][0] != patched[1][0]
        or not set(previous_bounds).issubset(current_bounds)
        or any(bound[0] != "!=" for bound in set(current_bounds) - set(previous_bounds))
        or not allows_published_release(previous_bounds, removed)
        or allows_published_release(current_bounds, removed)
        or not allows_published_release(current_bounds, patched)
    ):
        return False
    retained = {release for release in preserved if allows_published_release(previous_bounds, release)}
    if not retained or any(not allows_published_release(current_bounds, release) for release in retained):
        return False
    epoch, components, post = patched
    work = 0
    exclusions = {
        value
        for operator, bound_epoch, value, _, wildcard in current_bounds
        if operator == "!=" and wildcard and bound_epoch == epoch
    }
    for index in range(1, len(components)):
        if components[index] > 256 - work:
            return False
        for component in range(components[index]):
            work += 1
            prefix = components[:index] + (component,)
            if published_lower_bound_excludes(previous_bounds, epoch, prefix):
                continue
            if not any(
                len(exclusion) <= len(prefix) and prefix[: len(exclusion)] == exclusion for exclusion in exclusions
            ):
                return False
    if post >= 0:
        if post + 1 > 256 - work:
            return False
        if allows_published_release(current_bounds, (epoch, components, -1)):
            return False
        for earlier in range(post):
            if allows_published_release(current_bounds, (epoch, components, earlier)):
                return False
    return True


def secures_supported_published_branches(
    previous_domains: ResolutionDomains,
    current_domains: ResolutionDomains,
    previous_published: ContextRequirements,
    current_published: ContextRequirements,
    previous_protected: ContextRequirements,
    current_protected: ContextRequirements,
) -> bool:
    if not preserves_supported_security_branches(
        previous_domains, current_domains, previous_protected, current_protected
    ):
        return False
    observed = False
    for domain in previous_domains.keys() | current_domains.keys():
        prior_versions = previous_domains.get(domain, set())
        updated_versions = current_domains.get(domain, set())
        if prior_versions == updated_versions:
            continue
        removed = sorted(stable_version(value) for value in prior_versions - updated_versions)
        patched = sorted(stable_version(value) for value in updated_versions - prior_versions)
        retained = {stable_version(value) for value in prior_versions & updated_versions}
        if len(removed) != len(patched):
            return False
        for old, new in zip(removed, patched, strict=True):
            covered = False
            for context, previous in previous_published.items():
                current = current_published.get(context, set())
                if len(previous) != 1 or len(current) != 1 or not marker_overlap(context[3], domain):
                    continue
                before = published_bounds(next(iter(previous)))
                if not allows_published_release(before, old):
                    continue
                after = published_bounds(next(iter(current)))
                preserved = retained | {release for release in patched if release != new}
                if not excludes_affected_published_branch(before, after, old, new, preserved):
                    return False
                covered = True
            if not covered:
                return False
            observed = True
    return observed


def covers_transitive_security_release(
    requirements: ContextRequirements,
    domain: MarkerContext,
    fragments: tuple[MarkerContext, ...],
    removed: StableRelease,
    patched: StableRelease,
    current_domains: ResolutionDomains,
) -> bool:
    covered: list[MarkerContext] = []
    for context, declarations in requirements.items():
        if not any(marker_overlap(context[3], fragment) for fragment in fragments):
            continue
        for requirement in declarations:
            bounds = published_bounds(requirement)
            floors = minimums({requirement}, allow_missing=True, exact=True)
            reviewed_floor = len(floors) == 1 and floors[0] >= patched
            reviewed_series = any(
                operator == "!="
                and wildcard
                and epoch == removed[0]
                and len(prefix) <= len(removed[1])
                and removed[1][: len(prefix)] == prefix
                for operator, epoch, prefix, _, wildcard in bounds
            )
            if not reviewed_floor and not reviewed_series:
                continue
            if not allows_published_release(bounds, patched) or allows_published_release(bounds, removed):
                continue
            if any(
                (other != domain or not reviewed_floor)
                and marker_overlap(context[3], other)
                and any(not allows_published_release(bounds, stable_version(version)) for version in versions)
                for other, versions in current_domains.items()
            ):
                continue
            covered.append(context[3])
    return bool(covered) and all(
        not uncovered_marker_fragments(fragment, covered, anchor_platform_release=True) for fragment in fragments
    )


def preserves_additive_supported_releases(
    context: DependencyContext,
    bounds: tuple[PublishedBound, ...],
    previous_contexts: ContextRequirements,
    previous_domains: ResolutionDomains,
    current_domains: ResolutionDomains,
) -> bool:
    global_scope = context[0] in {"uv-constraint", "uv-build-constraint"}
    for current_domain, versions in current_domains.items():
        if not marker_overlap(context[3], current_domain):
            continue
        for version in versions:
            release = stable_version(version)
            if allows_published_release(bounds, release):
                continue
            for previous_domain, previous_versions in previous_domains.items():
                if not any(stable_version(previous) == release for previous in previous_versions):
                    continue
                shared = tuple(sorted(context[3] + previous_domain))
                if not marker_overlap(shared, current_domain):
                    continue
                if global_scope:
                    return False
                for original, declarations in previous_contexts.items():
                    if original[:2] != context[:2] or not matches_protected_release(declarations, release):
                        continue
                    if marker_overlap(tuple(sorted(shared + original[3])), current_domain):
                        return False
    return True


def reviewed_additive_protected_contexts(
    previous_contexts: ContextRequirements,
    current_contexts: ContextRequirements,
    previous_domains: ResolutionDomains,
    current_domains: ResolutionDomains,
) -> bool:
    additions = set(current_contexts) - set(previous_contexts)
    if not additions:
        return False
    for context in additions:
        for requirement in current_contexts[context]:
            floors = minimums({requirement}, allow_missing=True, exact=True)
            if len(floors) != 1:
                return False
            bounds = published_bounds(requirement)
            reviewed = False
            for domain in previous_domains.keys() | current_domains.keys():
                previous_versions = previous_domains.get(domain, set())
                current_versions = current_domains.get(domain, set())
                if previous_versions == current_versions or not marker_overlap(context[3], domain):
                    continue
                removed = sorted(stable_version(version) for version in previous_versions - current_versions)
                patched = sorted(stable_version(version) for version in current_versions - previous_versions)
                if len(removed) != len(patched):
                    continue
                for previous, current in zip(removed, patched, strict=True):
                    if (
                        current <= previous
                        or floors[0] < current
                        or not allows_published_release(bounds, current)
                        or allows_published_release(bounds, previous)
                    ):
                        continue
                    prior = [
                        original[3]
                        for original, declarations in previous_contexts.items()
                        for declaration in declarations
                        if minimums({declaration}, allow_missing=True, exact=True)
                        and matches_protected_release({declaration}, previous)
                    ]
                    fragments = uncovered_marker_fragments(domain, prior)
                    if not any(marker_overlap(context[3], fragment) for fragment in fragments):
                        continue
                    if any(
                        other != domain
                        and marker_overlap(context[3], other)
                        and any(not allows_published_release(bounds, stable_version(version)) for version in versions)
                        for other, versions in current_domains.items()
                    ) or not preserves_additive_supported_releases(
                        context, bounds, previous_contexts, previous_domains, current_domains
                    ):
                        continue
                    reviewed = True
                    break
                if reviewed:
                    break
            if not reviewed:
                return False
    return True


old_project = read_base("pyproject.toml")
old_lock = read_base("uv.lock")
new_project = cast(dict[str, Any], tomllib.loads(pathlib.Path("pyproject.toml").read_text()))
new_lock = cast(dict[str, Any], tomllib.loads(pathlib.Path("uv.lock").read_text()))
old_direct, old_contexts = direct(old_project)
new_direct, new_contexts = direct(new_project)
old_versions, old_resolution_contexts = versions(old_lock)
new_versions, new_resolution_contexts = versions(new_lock)
for name in old_resolution_contexts.keys() & new_resolution_contexts.keys():
    old_resolution_contexts[name], new_resolution_contexts[name] = reconcile_resolution_domains(
        old_resolution_contexts[name], new_resolution_contexts[name]
    )
old_protected, old_protected_contexts = direct(old_project, protected=True)
new_protected, new_protected_contexts = direct(new_project, protected=True)
new_requested_extra_contexts: list[tuple[str, DependencyContext]] = []
for name, contexts in new_contexts.items():
    previous_contexts = old_contexts.get(name, {})
    for context in contexts:
        if context[2] and not any(
            previous[:2] == context[:2] and set(context[2]).issubset(previous[2]) and previous[3] == context[3]
            for previous in previous_contexts
        ):
            new_requested_extra_contexts.append((name, context))
previous_reachable: dict[str, set[tuple[str, str, MarkerContext]]] = {}
extra_reachable: dict[str, set[tuple[str, str, MarkerContext]]] = {}
newly_exposed: set[str] = set()
if new_requested_extra_contexts:
    previous_reachable = published_reachability(old_lock, old_contexts)
    extra_reachable = requested_extra_reachability(new_lock, old_contexts, new_contexts, new_requested_extra_contexts)
    newly_exposed = {
        name
        for name, audiences in extra_reachable.items()
        for audience in audiences
        if not any(audience_covers(previous, audience) for previous in previous_reachable.get(name, set()))
        and not any(
            root == name and audience_covers((context[0], context[1], context[3]), audience)
            for root, context in new_requested_extra_contexts
        )
    }
partitioned_security_sources: set[tuple[bool, str]] = set()
for is_protected, previous_by_name, current_by_name in (
    (False, old_contexts, new_contexts),
    (True, old_protected_contexts, new_protected_contexts),
):
    for name, previous_contexts in previous_by_name.items():
        preserved, partitioned = preserves_requirement_source_markers(
            previous_contexts,
            current_by_name.get(name, {}),
            old_resolution_contexts.get(name, {}),
            new_resolution_contexts.get(name, {}),
            extra_review=is_protected and name in newly_exposed,
        )
        if not preserved:
            message = (
                "Do not widen or narrow an existing security dependency marker for "
                if is_protected
                else "Do not remove a published direct dependency or its original context for "
            )
            raise SystemExit(message + name)
        if partitioned:
            partitioned_security_sources.add((is_protected, name))
for name, previous in old_protected.items():
    requirements = new_protected.get(name, set())
    previous_contexts = old_protected_contexts.get(name, {})
    current_contexts = new_protected_contexts.get(name, {})
    previous_domains = old_resolution_contexts.get(name, {})
    current_domains = new_resolution_contexts.get(name, {})
    if previous == requirements and previous_contexts == current_contexts and previous_domains == current_domains:
        continue
    if previous != requirements or previous_contexts != current_contexts:
        security_replacements: ContextReplacements = {
            context: replacement_contexts(context, prior_requirements, current_contexts, previous_domains, exact=True)
            for context, prior_requirements in previous_contexts.items()
        }
        if not preserves_dependency_security_bounds(
            previous_contexts, security_replacements, previous_domains, current_domains
        ):
            raise SystemExit("Do not weaken a protected dependency security exclusion or upper bound for " + name)
    prior_minimums = minimums(previous, allow_missing=True, exact=True)
    if not prior_minimums:
        continue
    updated_minimums = minimums(requirements, exact=True)
    mapped_contexts: ContextReplacements = {}
    for context, prior_requirements in previous_contexts.items():
        context_minimums = minimums(prior_requirements, allow_missing=True, exact=True)
        if not context_minimums:
            continue
        replacements = replacement_contexts(context, prior_requirements, current_contexts, previous_domains, exact=True)
        if not replacements:
            raise SystemExit("Do not lower a contextual protected security minimum for " + name)
        mapped_contexts[context] = replacements
        for context_requirements in replacements.values():
            updated_context_minimums = minimums(context_requirements, exact=True)
            if len(updated_context_minimums) != len(context_minimums) or any(
                updated < previous for previous, updated in zip(context_minimums, updated_context_minimums, strict=True)
            ):
                raise SystemExit("Do not lower a contextual protected security minimum for " + name)
    split = (
        any(context not in replacements for context, replacements in mapped_contexts.items())
        or (True, name) in partitioned_security_sources
    )
    if split:
        if set(current_contexts) != {
            replacement for replacements in mapped_contexts.values() for replacement in replacements
        }:
            raise SystemExit("Do not replace a protected security dependency context for " + name)
    elif len(updated_minimums) != len(prior_minimums) or any(
        updated < previous for previous, updated in zip(prior_minimums, updated_minimums, strict=True)
    ):
        if (
            name in old_direct
            or name in new_direct
            or not reviewed_additive_protected_contexts(
                previous_contexts, current_contexts, previous_domains, current_domains
            )
        ):
            raise SystemExit("Do not lower a protected dependency security minimum for " + name)
    if previous_domains == current_domains:
        continue
    protected_patched_domains: dict[MarkerContext, list[tuple[StableRelease, StableRelease]]] = {}
    for domain in previous_domains.keys() | current_domains.keys():
        prior_versions = previous_domains.get(domain, set())
        updated_versions = current_domains.get(domain, set())
        if prior_versions == updated_versions:
            continue
        introduced = sorted(stable_version(version) for version in updated_versions - prior_versions)
        removed = sorted(stable_version(version) for version in prior_versions - updated_versions)
        if (
            not introduced
            or len(introduced) != len(removed)
            or any(updated <= previous for previous, updated in zip(removed, introduced, strict=True))
        ):
            raise SystemExit("Missing contextual upgraded protected security dependency release for " + name)
        protected_patched_domains[domain] = list(zip(removed, introduced, strict=True))
    for context, prior_requirements in previous_contexts.items():
        prior_context_minimums = minimums(prior_requirements, allow_missing=True, exact=True)
        if not prior_context_minimums:
            continue
        for replacement, context_requirements in mapped_contexts[context].items():
            patched = [
                introduced
                for domain, upgrades in protected_patched_domains.items()
                if marker_overlap(replacement[3], domain)
                for removed, introduced in upgrades
                if matches_protected_release(prior_requirements, removed)
            ]
            if not patched:
                continue
            updated_context_minimums = minimums(context_requirements, exact=True)
            if (
                not updated_context_minimums
                or any(updated < max(patched) for updated in updated_context_minimums)
                or any(
                    not matches_protected_release(context_requirements, release, upper_only=True) for release in patched
                )
            ):
                raise SystemExit("Raise the contextual protected security minimum to the patched release for " + name)

for name in old_versions.keys() & new_versions.keys():
    if name in old_direct or name in new_direct:
        continue
    previous_contexts = old_protected_contexts.get(name, {})
    previous_domains = old_resolution_contexts.get(name, {})
    current_domains = new_resolution_contexts.get(name, {})
    for domain in previous_domains.keys() | current_domains.keys():
        prior_versions = previous_domains.get(domain, set())
        updated_versions = current_domains.get(domain, set())
        if prior_versions == updated_versions or not updated_versions:
            continue
        removed = sorted(stable_version(version) for version in prior_versions - updated_versions)
        introduced = sorted(stable_version(version) for version in updated_versions - prior_versions)
        if not introduced:
            continue
        if (
            not removed
            or len(introduced) != len(removed)
            or any(updated <= previous for previous, updated in zip(removed, introduced, strict=True))
        ):
            raise SystemExit("Missing contextual upgraded transitive security dependency release for " + name)
        for removed_release, patched_release in zip(removed, introduced, strict=True):
            protected = [
                context[3]
                for context, declarations in previous_contexts.items()
                for declaration in declarations
                if minimums({declaration}, allow_missing=True, exact=True)
                and matches_protected_release({declaration}, removed_release)
            ]
            fragments = uncovered_marker_fragments(domain, protected, anchor_platform_release=True)
            if fragments and not covers_transitive_security_release(
                new_protected_contexts.get(name, {}),
                domain,
                fragments,
                removed_release,
                patched_release,
                current_domains,
            ):
                raise SystemExit("Add a reviewed contextual transitive security dependency boundary for " + name)

if new_requested_extra_contexts:
    for name in newly_exposed:
        reviewed_contexts = new_protected_contexts.get(name, {}) | new_contexts.get(name, {})
        for domain, domain_versions in new_resolution_contexts.get(name, {}).items():
            exposed: set[tuple[str, str, MarkerContext]] = set()
            for scope, group, marker in extra_reachable.get(name, set()):
                if not marker_overlap(marker, domain):
                    continue
                shared = tuple(sorted(set(marker + domain)))
                prior = [
                    previous_marker
                    for previous_scope, previous_group, previous_marker in previous_reachable.get(name, set())
                    if previous_scope == "runtime" or (previous_scope, previous_group) == (scope, group)
                ]
                exposed.update((scope, group, fragment) for fragment in uncovered_marker_fragments(shared, prior))
            if not exposed:
                continue
            for version in domain_versions:
                release = stable_version(version)
                for scope, group, fragment in exposed:
                    extra_coverings: list[MarkerContext] = []
                    for context, requirements in reviewed_contexts.items():
                        if context[0] == "optional" and context[:2] != (scope, group):
                            continue
                        if not marker_overlap(context[3], fragment):
                            continue
                        for requirement in requirements:
                            floors = minimums({requirement}, allow_missing=True, exact=True)
                            if (
                                len(floors) == 1
                                and floors[0] >= release
                                and allows_published_release(published_bounds(requirement), release)
                            ):
                                extra_coverings.append(context[3])
                    if not extra_coverings or uncovered_marker_fragments(
                        fragment, extra_coverings, anchor_platform_release=True
                    ):
                        raise SystemExit(
                            "Review the contextual dependency introduced by a newly requested extra for " + name
                        )

direct_replacements: dict[str, ContextReplacements] = {}
for name, previous_contexts in old_contexts.items():
    current_contexts = new_contexts.get(name, {})
    mapped_contexts = {}
    for context, previous_requirements in previous_contexts.items():
        replacements = replacement_contexts(
            context, previous_requirements, current_contexts, old_resolution_contexts.get(name, {})
        )
        if not replacements:
            raise SystemExit("Do not remove a published direct dependency or its original context for " + name)
        mapped_contexts[context] = replacements
    if any(context not in replacements for context, replacements in mapped_contexts.items()) and set(
        current_contexts
    ) != {replacement for replacements in mapped_contexts.values() for replacement in replacements}:
        raise SystemExit("Do not replace a published direct dependency context for " + name)
    direct_replacements[name] = mapped_contexts
for name, requirements in new_direct.items():
    previous = old_direct.get(name, set())
    previous_contexts = old_contexts.get(name, {})
    current_contexts = new_contexts.get(name, {})
    if previous != requirements or previous_contexts != current_contexts:
        previous_minimums = minimums(previous, allow_missing=True)
        if previous_minimums:
            mapped_contexts = direct_replacements.get(name, {})
            retained_requirements = {
                requirement
                for replacements in mapped_contexts.values()
                for updated in replacements.values()
                for requirement in updated
            }
            updated_minimums = minimums(retained_requirements or requirements)
            split = (
                any(context not in replacements for context, replacements in mapped_contexts.items())
                or (False, name) in partitioned_security_sources
            )
            if not split and (
                len(updated_minimums) != len(previous_minimums)
                or any(
                    updated < previous for previous, updated in zip(previous_minimums, updated_minimums, strict=True)
                )
            ):
                raise SystemExit("Do not lower a published security-fixed minimum for " + name)
            for context, prior_requirements in previous_contexts.items():
                prior_minimums = minimums(prior_requirements, allow_missing=True)
                if not prior_minimums:
                    continue
                for context_requirements in mapped_contexts[context].values():
                    context_minimums = minimums(context_requirements)
                    if len(context_minimums) != len(prior_minimums) or any(
                        updated < previous for previous, updated in zip(prior_minimums, context_minimums, strict=True)
                    ):
                        raise SystemExit("Do not lower a contextual security-fixed minimum for " + name)
    previous_domains = old_resolution_contexts.get(name, {})
    current_domains = new_resolution_contexts.get(name, {})
    if (previous != requirements or previous_contexts != current_contexts) and not preserves_dependency_security_bounds(
        previous_contexts, direct_replacements.get(name, {}), previous_domains, current_domains
    ):
        raise SystemExit("Do not weaken a published security exclusion or upper bound for " + name)
    if old_versions.get(name, set()) == new_versions.get(name, set()) and previous_domains == current_domains:
        continue
    if previous == requirements:
        raise SystemExit("Raise the published security-fixed minimum for " + name)
    if secures_supported_published_branches(
        previous_domains,
        current_domains,
        previous_contexts,
        current_contexts,
        old_protected_contexts.get(name, {}),
        new_protected_contexts.get(name, {}),
    ):
        continue
    patched_domains: dict[MarkerContext, StableRelease] = {}
    for domain in previous_domains.keys() | current_domains.keys():
        prior_versions = previous_domains.get(domain, set())
        updated_versions = current_domains.get(domain, set())
        if prior_versions == updated_versions:
            continue
        introduced = sorted(stable_version(version) for version in updated_versions - prior_versions)
        removed = sorted(stable_version(version) for version in prior_versions - updated_versions)
        if (
            not introduced
            or len(introduced) != len(removed)
            or any(updated <= previous for previous, updated in zip(removed, introduced, strict=True))
        ):
            raise SystemExit("Missing contextual upgraded security dependency release for " + name)
        patched_domains[domain] = introduced[-1]
    if not patched_domains:
        raise SystemExit("Missing upgraded direct security dependency release for " + name)
    covered: set[MarkerContext] = set()
    for context, context_requirements in current_contexts.items():
        domains = {domain for domain in patched_domains if marker_overlap(context[3], domain)}
        if not domains:
            continue
        covered.update(domains)
        patched_minimum = max(patched_domains[domain] for domain in domains)
        updated_minimums = minimums(context_requirements, exact=True)
        original_context = next(
            (
                original
                for original, replacements in direct_replacements.get(name, {}).items()
                if context in replacements
            ),
            context,
        )
        previous_minimums = minimums(previous_contexts.get(original_context, set()), allow_missing=True, exact=True)
        if (
            not updated_minimums
            or any(updated < patched_minimum for updated in updated_minimums)
            or previous_minimums
            and (len(updated_minimums) != len(previous_minimums) or updated_minimums[0] <= previous_minimums[0])
        ):
            raise SystemExit("Raise the contextual security-fixed minimum for " + name)
    if covered != set(patched_domains):
        raise SystemExit("Raise the published security-fixed minimum for " + name)
