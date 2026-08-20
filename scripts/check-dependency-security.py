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


def marker_context(marker: str) -> MarkerContext:
    if not marker.strip():
        return ()
    try:
        if any(
            token.type == tokenize.OP and token.string in {"(", ")"}
            for token in tokenize.generate_tokens(io.StringIO(marker).readline)
        ):
            raise ValueError("Parenthesized security dependency marker")
        expression = ast.parse(marker.strip(), mode="eval").body
    except (SyntaxError, tokenize.TokenError, ValueError):
        raise SystemExit("Ambiguous direct security dependency marker") from None
    if isinstance(expression, ast.BoolOp):
        if not isinstance(expression.op, ast.And):
            raise SystemExit("Ambiguous direct security dependency marker")
        parts = expression.values
    else:
        parts = [expression]
    result: list[MarkerClause] = []
    for part in parts:
        if (
            not isinstance(part, ast.Compare)
            or not isinstance(part.left, ast.Name)
            or len(part.ops) != 1
            or len(part.comparators) != 1
            or not isinstance(part.comparators[0], ast.Constant)
            or not isinstance(part.comparators[0].value, str)
            or type(part.ops[0]) not in {ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn}
        ):
            raise SystemExit("Ambiguous direct security dependency marker")
        result.append((part.left.id.lower(), type(part.ops[0]).__name__, part.comparators[0].value))
    return tuple(sorted(result))


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
            context = (scope, group, requested, marker_context(match.group(3).partition(";")[2]))
            normalized = name + (match.group(2) or "").lower() + re.sub(r"\s+", "", match.group(3)).lower()
            result.setdefault(name, set()).add(normalized)
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


def stable_version(value: str) -> StableRelease:
    match = re.fullmatch(r"(?:(\d+)!)?(\d+(?:\.\d+)*)(?:\.post(\d+))?", value)
    if match is None:
        raise SystemExit("Unsupported direct security dependency minimum")
    release = tuple(int(part) for part in match.group(2).split("."))
    while release and release[-1] == 0:
        release = release[:-1]
    post = -1 if match.group(3) is None else int(match.group(3))
    return int(match.group(1) or 0), release, post


def simple_marker_overlap(requirement: MarkerContext, resolution: MarkerContext) -> bool:
    clauses: dict[str, list[MarkerClause]] = {}
    for variable, operator, value in requirement + resolution:
        family = "python" if variable in {"python_version", "python_full_version"} else variable
        clauses.setdefault(family, []).append((variable, operator, value))
    for family, constraints in clauses.items():
        if family == "python":
            lower: tuple[int, int, int] = (0, 0, 0)
            upper: tuple[int, int, int] | None = None
            excluded: list[tuple[tuple[int, int, int], tuple[int, int, int]]] = []
            for variable, operator, value in constraints:
                match = re.fullmatch(r"(\d+)\.(\d+)(?:\.(\d+))?(\.\*)?", value)
                if match is None or (variable == "python_version" and match.group(3) is not None):
                    raise SystemExit("Ambiguous Python security dependency marker")
                major, minor = int(match.group(1)), int(match.group(2))
                patch = int(match.group(3) or 0)
                wildcard = match.group(4) is not None
                if wildcard and operator not in {"Eq", "NotEq"}:
                    raise SystemExit("Ambiguous wildcard security dependency marker")
                start = (major, minor, patch)
                stop = (major, minor + 1, 0) if variable == "python_version" or wildcard else (major, minor, patch + 1)
                if operator == "Eq":
                    lower = max(lower, start)
                    upper = stop if upper is None else min(upper, stop)
                elif operator == "NotEq":
                    excluded.append((start, stop))
                elif operator == "Lt":
                    upper = start if upper is None else min(upper, start)
                elif operator == "LtE":
                    upper = stop if upper is None else min(upper, stop)
                elif operator == "Gt":
                    lower = max(lower, stop)
                elif operator == "GtE":
                    lower = max(lower, start)
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
                "platform_python_implementation",
                "implementation_name",
                "extra",
            }:
                raise SystemExit("Unsupported security dependency marker variable")
            equality: str | None = None
            exclusions: set[str] = set()
            for _, operator, value in constraints:
                if operator == "Eq":
                    if equality is not None and equality != value:
                        return False
                    equality = value
                elif operator == "NotEq":
                    exclusions.add(value)
                else:
                    raise SystemExit("Ambiguous platform security dependency marker")
            if equality is not None and equality in exclusions:
                return False
    return True


def marker_options(context: MarkerContext) -> list[MarkerContext]:
    options: list[MarkerContext] = [()]
    allowed_platforms = {
        "sys_platform",
        "os_name",
        "platform_system",
        "platform_machine",
        "platform_python_implementation",
        "implementation_name",
        "extra",
    }
    for variable, operator, value in context:
        if operator not in {"In", "NotIn"}:
            options = [option + ((variable, operator, value),) for option in options]
            continue
        if variable == "python_version":
            pattern = r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
        elif variable == "python_full_version":
            pattern = r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
        elif variable in allowed_platforms:
            pattern = r"[A-Za-z0-9][A-Za-z0-9_.-]*"
        else:
            raise SystemExit("Unsupported security dependency membership marker variable")
        values = tuple(item.strip() for item in value.split(","))
        if (
            not values
            or len(values) > 16
            or len(set(values)) != len(values)
            or any(not re.fullmatch(pattern, item) for item in values)
            or any(
                first in second or second in first
                for index, first in enumerate(values)
                for second in values[index + 1 :]
            )
        ):
            raise SystemExit("Ambiguous security dependency membership marker")
        if operator == "In":
            options = [option + ((variable, "Eq", member),) for option in options for member in values]
        else:
            exclusions = tuple((variable, "NotEq", member) for member in values)
            options = [option + exclusions for option in options]
        if len(options) > 64:
            raise SystemExit("Ambiguous security dependency membership marker")
    return options


def marker_overlap(requirement: MarkerContext, resolution: MarkerContext) -> bool:
    requirements, resolutions = marker_options(requirement), marker_options(resolution)
    if len(requirements) * len(resolutions) > 128:
        raise SystemExit("Ambiguous security dependency membership marker")
    return any(simple_marker_overlap(left, right) for left in requirements for right in resolutions)


def minimums(requirements: set[str], *, allow_missing: bool = False, exact: bool = False) -> list[StableRelease]:
    result: list[StableRelease] = []
    for requirement in requirements:
        specifier = requirement.split(";", 1)[0]
        pattern = r"(?<![<>=!~])(?:>=|>|==)([^,;]+)" if exact else r"(?<![<>=!~])(?:>=|>)([^,;]+)"
        matches = re.findall(pattern, specifier)
        if len(matches) != 1:
            if allow_missing and not matches:
                continue
            raise SystemExit("Missing or ambiguous direct security dependency minimum")
        result.append(stable_version(matches[0].strip()))
    return sorted(result)


def matches_protected_release(requirements: set[str], release: StableRelease, *, upper_only: bool = False) -> bool:
    for requirement in requirements:
        expression = requirement.split(";", 1)[0]
        match = re.fullmatch(r"\s*([A-Za-z0-9][A-Za-z0-9_.-]*)(\[[^\]]+\])?\s*(.*)", expression)
        if match is None:
            raise SystemExit("Ambiguous protected security dependency requirement")
        accepted = True
        for clause in match.group(3).split(","):
            if not clause.strip():
                continue
            bound = re.fullmatch(r"(>=|<=|==|!=|>|<)\s*(\S+)", clause.strip())
            if bound is None:
                raise SystemExit("Ambiguous protected security dependency bound")
            operator, value = bound.group(1), stable_version(bound.group(2))
            if upper_only and operator in {">=", ">"}:
                continue
            if (
                operator == ">="
                and release < value
                or operator == ">"
                and release <= value
                or operator == "<="
                and release > value
                or operator == "<"
                and release >= value
                or operator == "=="
                and release != value
                or operator == "!="
                and release == value
            ):
                accepted = False
        if accepted:
            return True
    return False


def unchanged_nonfloor_bounds(requirement: str) -> tuple[tuple[str, StableRelease], ...]:
    expression = requirement.split(";", 1)[0]
    match = re.fullmatch(r"\s*([A-Za-z0-9][A-Za-z0-9_.-]*)(\[[^\]]+\])?\s*(.*)", expression)
    if match is None:
        raise SystemExit("Ambiguous split security dependency requirement")
    bounds: list[tuple[str, StableRelease]] = []
    for clause in match.group(3).split(","):
        if not clause.strip():
            continue
        bound = re.fullmatch(r"(>=|<=|==|!=|>|<)\s*(\S+)", clause.strip())
        if bound is None:
            raise SystemExit("Ambiguous split security dependency bound")
        operator, value = bound.group(1), stable_version(bound.group(2))
        if operator not in {">=", ">", "=="}:
            bounds.append((operator, value))
    return tuple(sorted(bounds))


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
    if current or previous_context[3] or len(previous_requirements) != 1:
        return {}
    original = next(iter(previous_requirements))
    original_minimums = minimums(previous_requirements, allow_missing=True, exact=exact)
    if len(original_minimums) != 1:
        return {}
    replacements = {
        context: requirements
        for context, requirements in current_contexts.items()
        if context[:3] == previous_context[:3] and context[3]
    }
    if len(replacements) < 2:
        return {}
    for requirements in replacements.values():
        if len(requirements) != 1:
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
        if any(matches_protected_release(previous_requirements, stable_version(version)) for version in versions)
    }
    if len(relevant) < 2:
        return {}
    covered: set[DependencyContext] = set()
    opposite = {
        "Eq": "NotEq",
        "NotEq": "Eq",
        "Lt": "GtE",
        "LtE": "Gt",
        "Gt": "LtE",
        "GtE": "Lt",
        "In": "NotIn",
        "NotIn": "In",
    }
    for domain in relevant:
        matched = [context for context in replacements if marker_overlap(context[3], domain)]
        if len(matched) != 1:
            return {}
        for variable, operator, value in matched[0][3]:
            if operator not in opposite or marker_overlap(domain, ((variable, opposite[operator], value),)):
                return {}
        covered.add(matched[0])
    return replacements if covered == set(replacements) else {}


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
        if not unchanged or not removed or len(removed) != len(introduced):
            return False
        observed = True
        for previous_release, patched_release in zip(removed, introduced, strict=True):
            if patched_release <= previous_release:
                return False
            supported = False
            for context, previous_requirements in previous_contexts.items():
                requirements = current_contexts.get(context, set())
                if len(previous_requirements) != 1 or len(requirements) != 1 or not marker_overlap(context[3], domain):
                    continue
                original = next(iter(previous_requirements))
                replacement = next(iter(requirements))
                bounds = unchanged_nonfloor_bounds(original)
                if (
                    not any(operator in {"<", "<="} for operator, _ in bounds)
                    or unchanged_nonfloor_bounds(replacement) != bounds
                    or not matches_protected_release(previous_requirements, previous_release)
                    or not matches_protected_release(requirements, patched_release)
                ):
                    continue
                before = minimums(previous_requirements, allow_missing=True, exact=True)
                after = minimums(requirements, exact=True)
                if len(before) != 1 or len(after) != 1 or after[0] < patched_release or after[0] <= before[0]:
                    continue
                if not any(
                    not matches_protected_release(previous_requirements, preserved)
                    and any(
                        other != context
                        and marker_overlap(other[3], domain)
                        and other in current_contexts
                        and matches_protected_release(protected, preserved)
                        and matches_protected_release(current_contexts[other], preserved)
                        for other, protected in previous_contexts.items()
                    )
                    for preserved in unchanged
                ):
                    continue
                supported = True
                break
            if not supported:
                return False
    return observed


def published_bounds(requirement: str) -> tuple[PublishedBound, ...]:
    expression = requirement.split(";", 1)[0]
    match = re.fullmatch(r"\s*([A-Za-z0-9][A-Za-z0-9_.-]*)(\[[^\]]+\])?\s*(.*)", expression)
    if match is None:
        raise SystemExit("Ambiguous published security dependency requirement")
    clauses = match.group(3).split(",")
    if len(clauses) > 256:
        raise SystemExit("Unbounded published security dependency exclusions")
    result: list[PublishedBound] = []
    for clause in clauses:
        match = re.fullmatch(
            r"(>=|<=|==|!=|>|<)\s*((?:(\d+)!)?(\d+(?:\.\d+)*)(?:\.post(\d+))?)(\.\*)?",
            clause.strip(),
        )
        if match is None or len(match.group(2)) > 128:
            raise SystemExit("Ambiguous published security dependency bound")
        components = match.group(4).split(".")
        if len(components) > 16 or any(len(component) > 9 for component in components):
            raise SystemExit("Unbounded published security dependency release")
        wildcard = match.group(6) is not None
        if wildcard and (match.group(1) != "!=" or match.group(5) is not None):
            raise SystemExit("Ambiguous published security dependency wildcard")
        epoch, release, post = stable_version(match.group(2))
        prefix = tuple(int(component) for component in components)
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
            and release <= bound
            or operator == "<="
            and release > bound
            or operator == "<"
            and release >= bound
            or operator == "=="
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
            if candidate_wildcard or updated not in {">", ">=", "=="}:
                continue
            bound = candidate_epoch, candidate, candidate_post
            if bound > limit or bound == limit and (operator == ">=" or updated == ">"):
                return True
        return False
    if operator in {"<", "<="}:
        limit = epoch, components, post
        for updated, candidate_epoch, candidate, candidate_post, candidate_wildcard in current:
            if candidate_wildcard or updated not in {"<", "<=", "=="}:
                continue
            bound = candidate_epoch, candidate, candidate_post
            if bound < limit or bound == limit and (operator == "<=" or updated == "<"):
                return True
        return False
    if operator == "==":
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
        if updated == "==":
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
    if operator != "==" or wildcard:
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
        operator == "==" and not wildcard and (epoch, components, post) == patched
        for operator, epoch, components, post, wildcard in current
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
            if not any(re.match(r"(?:!=|<=|<|>=|>|==)", clause.strip()) for clause in clauses):
                continue
            before = published_bounds(requirement)
            protected = tuple(bound for bound in before if bound[0] in {"<", "<=", "!=", ">", ">=", "=="})
            preserve_releases = any(bound[0] in {"<", "<=", "!=", "=="} for bound in protected)
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
                        if bound[0] == "=="
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
        if not retained or len(removed) != len(patched):
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
                if not excludes_affected_published_branch(before, after, old, new, retained):
                    return False
                covered = True
            if not covered:
                return False
            observed = True
    return observed


def covers_transitive_security_release(
    requirements: ContextRequirements,
    domain: MarkerContext,
    removed: StableRelease,
    patched: StableRelease,
    current_domains: ResolutionDomains,
) -> bool:
    for context, declarations in requirements.items():
        if not marker_overlap(context[3], domain):
            continue
        for requirement in declarations:
            floors = minimums({requirement}, allow_missing=True, exact=True)
            if len(floors) != 1 or floors[0] < patched:
                continue
            bounds = published_bounds(requirement)
            if not allows_published_release(bounds, patched) or allows_published_release(bounds, removed):
                continue
            if any(
                other != domain
                and marker_overlap(context[3], other)
                and any(not allows_published_release(bounds, stable_version(version)) for version in versions)
                for other, versions in current_domains.items()
            ):
                continue
            return True
    return False


old_project = read_base("pyproject.toml")
old_lock = read_base("uv.lock")
new_project = cast(dict[str, Any], tomllib.loads(pathlib.Path("pyproject.toml").read_text()))
new_lock = cast(dict[str, Any], tomllib.loads(pathlib.Path("uv.lock").read_text()))
old_direct, old_contexts = direct(old_project)
new_direct, new_contexts = direct(new_project)
old_versions, old_resolution_contexts = versions(old_lock)
new_versions, new_resolution_contexts = versions(new_lock)
old_protected, old_protected_contexts = direct(old_project, protected=True)
new_protected, new_protected_contexts = direct(new_project, protected=True)
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
    split = any(context not in replacements for context, replacements in mapped_contexts.items())
    if split:
        if set(current_contexts) != {
            replacement for replacements in mapped_contexts.values() for replacement in replacements
        }:
            raise SystemExit("Do not replace a protected security dependency context for " + name)
    elif len(updated_minimums) != len(prior_minimums) or any(
        updated < previous for previous, updated in zip(prior_minimums, updated_minimums, strict=True)
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
    if any(minimums(requirements, allow_missing=True, exact=True) for requirements in previous_contexts.values()):
        continue
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
            if not covers_transitive_security_release(
                new_protected_contexts.get(name, {}), domain, removed_release, patched_release, current_domains
            ):
                raise SystemExit("Add a reviewed contextual transitive security dependency boundary for " + name)

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
            updated_minimums = minimums(requirements)
            mapped_contexts = direct_replacements.get(name, {})
            split = any(context not in replacements for context, replacements in mapped_contexts.items())
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
