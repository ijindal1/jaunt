"""Dependency graph helpers.

This module builds a spec-level dependency graph from decorator metadata and
optionally infers additional edges from best-effort AST analysis.

Graph representation convention:
- A graph is a dict[node, set[dep_nodes]] (edges point to dependencies).
- Toposort returns a list where dependencies come before dependents.
"""

from __future__ import annotations

import ast
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

from jaunt.errors import JauntDependencyCycleError
from jaunt.registry import SpecEntry
from jaunt.spec_ref import SpecRef, normalize_spec_ref, spec_ref_from_object

K = TypeVar("K")


def _iter_deps_value(value: object) -> Iterable[object]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple, set, frozenset)):
        return value
    return (value,)


def _normalize_dep(dep: object) -> SpecRef | None:
    try:
        # SpecRef is a NewType over str, so treat it as a str at runtime.
        if isinstance(dep, str):
            return normalize_spec_ref(dep)
        return spec_ref_from_object(dep)
    except Exception:
        # Best-effort: ignore anything we cannot normalize.
        return None


@dataclass(frozen=True, slots=True)
class _ModuleParse:
    source: str
    tree: ast.Module
    import_aliases: dict[str, str]
    from_imports: dict[str, str]


def _parse_module_once(path: str, *, cache: dict[str, _ModuleParse]) -> _ModuleParse | None:
    if path in cache:
        return cache[path]

    try:
        src = Path(path).read_text(encoding="utf-8")
        tree = ast.parse(src, filename=path)
    except Exception:
        return None

    import_aliases: dict[str, str] = {}
    from_imports: dict[str, str] = {}

    # Best-effort import tracking for simple name and attribute resolution.
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                bound = alias.asname or alias.name.split(".", 1)[0]
                import_aliases[bound] = alias.name
        elif isinstance(node, ast.ImportFrom):
            if not node.module:
                continue
            for alias in node.names:
                bound = alias.asname or alias.name
                # Store "pkg.mod:Name" style for easy comparison with SpecRef.
                from_imports[bound] = f"{node.module}:{alias.name}"

    parsed = _ModuleParse(
        source=src,
        tree=tree,
        import_aliases=import_aliases,
        from_imports=from_imports,
    )
    cache[path] = parsed
    return parsed


def _find_top_level_node(module: ast.Module, *, name: str) -> ast.AST | None:
    for node in module.body:
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and node.name == name
        ):
            return node
    return None


class _NameUseCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.names: set[str] = set()
        self.attr_roots: set[tuple[str, str]] = set()

    def visit_Name(self, node: ast.Name) -> None:  # noqa: N802 - ast API
        self.names.add(node.id)

    def visit_Attribute(self, node: ast.Attribute) -> None:  # noqa: N802 - ast API
        # Only resolve simple roots like `alias.Foo`, not deep chains.
        if isinstance(node.value, ast.Name):
            self.attr_roots.add((node.value.id, node.attr))
        self.generic_visit(node)


def build_spec_graph(
    specs: dict[SpecRef, SpecEntry],
    *,
    infer_default: bool,
) -> dict[SpecRef, set[SpecRef]]:
    """Build a dependency graph keyed by SpecRef.

    Explicit deps:
    - read from entry.decorator_kwargs["deps"]
    - normalize values to SpecRef; ignore unknown/missing deps (MVP)

    Inference (best-effort):
    - controlled by entry.decorator_kwargs["infer_deps"] override or infer_default
    - never raises for ordinary code; failures are treated as "no inferred deps"
    """

    graph: dict[SpecRef, set[SpecRef]] = {sr: set() for sr in specs}

    parse_cache: dict[str, _ModuleParse] = {}

    for spec_ref, entry in specs.items():
        deps_out = graph.setdefault(spec_ref, set())

        explicit = entry.decorator_kwargs.get("deps")
        for dep in _iter_deps_value(explicit):
            dep_ref = _normalize_dep(dep)
            if dep_ref is None or dep_ref == spec_ref:
                continue
            if dep_ref in specs:
                deps_out.add(dep_ref)

        infer_override = entry.decorator_kwargs.get("infer_deps")
        if infer_override is None:
            infer_enabled = infer_default
        else:
            infer_enabled = bool(infer_override)

        if not infer_enabled:
            continue

        # Inference is strictly best-effort; never fail the build because it
        # cannot parse or resolve names.
        try:
            if "." in entry.qualname:
                continue

            parsed = _parse_module_once(entry.source_file, cache=parse_cache)
            if parsed is None:
                continue

            node = _find_top_level_node(parsed.tree, name=entry.qualname)
            if node is None:
                continue

            collector = _NameUseCollector()
            collector.visit(node)

            inferred: set[SpecRef] = set()

            # 1) from-import direct names: `from x import Foo as Bar` then `Bar(...)`.
            for name in collector.names:
                dep = parsed.from_imports.get(name)
                if dep is not None:
                    dep_ref = normalize_spec_ref(dep)
                    if dep_ref in specs and dep_ref != spec_ref:
                        inferred.add(dep_ref)

            # 2) bare names: try same-module resolution (common for sibling defs/classes).
            for name in collector.names:
                candidate = SpecRef(f"{entry.module}:{name}")
                if candidate in specs and candidate != spec_ref:
                    inferred.add(candidate)

            # 3) attribute roots: `alias.Foo` where alias comes from `import pkg.mod as alias`.
            for root, attr in collector.attr_roots:
                mod = parsed.import_aliases.get(root)
                if not mod:
                    continue
                candidate = normalize_spec_ref(f"{mod}:{attr}")
                if candidate in specs and candidate != spec_ref:
                    inferred.add(candidate)

            deps_out.update(inferred)
        except Exception:
            continue

    return graph


def collapse_to_module_dag(spec_graph: dict[SpecRef, set[SpecRef]]) -> dict[str, set[str]]:
    """Collapse a spec dependency graph into a module-level graph."""

    module_graph: dict[str, set[str]] = {}

    def mod_of(sr: SpecRef) -> str:
        return str(sr).split(":", 1)[0]

    for sr, deps in spec_graph.items():
        m = mod_of(sr)
        module_graph.setdefault(m, set())
        for dep in deps:
            dm = mod_of(dep)
            module_graph.setdefault(dm, set())
            if dm != m:
                module_graph[m].add(dm)

    return module_graph


def toposort(graph: dict[K, set[K]]) -> list[K]:
    """Topologically sort a dependency graph (deps before dependents)."""

    perm: set[K] = set()
    temp: set[K] = set()
    order: list[K] = []
    stack: list[K] = []

    def visit(n: K) -> None:
        if n in perm:
            return
        if n in temp:
            # Extract a cycle path from the current recursion stack.
            try:
                i = stack.index(n)
            except ValueError:
                i = 0
            cycle = stack[i:] + [n]
            msg = "Dependency cycle detected: " + " -> ".join(str(x) for x in cycle)
            raise JauntDependencyCycleError(msg)

        temp.add(n)
        stack.append(n)
        for dep in sorted(graph.get(n, set()), key=lambda x: str(x)):
            visit(dep)
        stack.pop()
        temp.remove(n)
        perm.add(n)
        order.append(n)

    # Ensure nodes that only appear as deps are also considered.
    all_nodes: set[K] = set(graph.keys())
    for deps in graph.values():
        all_nodes.update(deps)

    for node in sorted(all_nodes, key=lambda x: str(x)):
        if node not in perm:
            visit(node)

    return order
