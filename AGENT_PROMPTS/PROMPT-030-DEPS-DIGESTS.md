# PROMPT-030: Dependency Graph + Digests (Incremental Rebuild Core) (L3)

Repo: `/Users/ishitajindal/Documents/jaunt`

## Depends On
- `PROMPT-010A` (`jaunt.errors`, `jaunt.spec_ref`)
- `PROMPT-010B` (`jaunt.registry`)

## Objective
Implement:
- spec-level dependency graph from explicit deps (+ best-effort inference, optional)
- module DAG collapse + topo sorting + cycle errors
- stable digests used for incremental rebuild decisions

Keep tests deterministic and fast; no discovery scanning; only temp file I/O for digest extraction.

## Owned Files (avoid editing anything else)
- `src/jaunt/deps.py`
- `src/jaunt/digest.py`
- `tests/test_deps.py`
- `tests/test_digest.py`

## Deliverables

### `src/jaunt/deps.py`
Implement:

- `build_spec_graph(specs: dict[SpecRef, SpecEntry], *, infer_default: bool) -> dict[SpecRef, set[SpecRef]]`
  - Explicit deps:
    - read from `entry.decorator_kwargs.get("deps")`
    - deps can be SpecRef strings or Python objects
    - normalize to SpecRefs (`normalize_spec_ref`, `spec_ref_from_object`)
    - if dep not in `specs`: ignore (MVP: do not crash)
  - Inference (optional, best-effort):
    - only if enabled for the entry (decorator override or `infer_default`)
    - parse module AST once per module file
    - extract referenced names in each top-level def/class body
    - resolve to known spec refs in `specs` when possible; ignore unknowns
    - inference must never raise for normal code; treat failures as “no inferred deps”

- `collapse_to_module_dag(spec_graph: dict[SpecRef, set[SpecRef]]) -> dict[str, set[str]]`
  - module for spec_ref is the left side of `":"`
  - add edges only when `module != dep_module`
  - ensure every module seen appears as a key (even if it has no deps)

- `toposort(graph: dict[K, set[K]]) -> list[K]`
  - return list with deps before dependents
  - on cycle: raise `JauntDependencyCycleError` and include a cycle path in the message

### `src/jaunt/digest.py`
Implement:

- `extract_source_segment(entry: SpecEntry) -> str`
  - read `entry.source_file`
  - `ast.parse`
  - find the top-level `FunctionDef`/`AsyncFunctionDef`/`ClassDef` with name == `entry.qualname`
  - return a stable, normalized source string:
    - use `ast.get_source_segment`
    - `textwrap.dedent`
    - normalize newlines to `\n`
    - strip trailing whitespace

- `local_digest(entry: SpecEntry) -> str`
  - sha256 hex of:
    - normalized source segment
    - plus stable JSON dump of decorator kwargs:
      - sort keys
      - convert any deps objects → SpecRef strings
      - ensure JSON-serializable (fallback: `str(x)` if needed)

- `graph_digest(spec_ref: SpecRef, specs: dict[SpecRef, SpecEntry], spec_graph: dict[SpecRef, set[SpecRef]], *, cache: dict[SpecRef, str] | None = None) -> str`
  - memoized recursion:
    - digest = sha256(local_digest + sorted(dep graph_digests))

- `module_digest(module_name: str, module_specs: list[SpecEntry], specs: dict[SpecRef, SpecEntry], spec_graph: dict[SpecRef, set[SpecRef]]) -> str`
  - sha256 hex of sorted graph_digests for specs in that module

## Tests

### `tests/test_deps.py`
Focus on explicit deps + topo/cycle behavior:
- explicit deps build correct spec graph edges
- collapse to module DAG is correct and has no self-edges
- toposort order respects deps
- cycle detection raises `JauntDependencyCycleError` and mentions participants

Inference can be untested in MVP or include 1 tiny smoke test; do not overbuild.

### `tests/test_digest.py`
Use tmp files:
- `local_digest` returns 64 hex chars and is deterministic
- source change alters `local_digest`
- `graph_digest` changes when a dependency’s source changes
- `module_digest` aggregates multiple specs deterministically

## Quality Gates
```bash
.venv/bin/python -m pytest -q tests/test_deps.py tests/test_digest.py
.venv/bin/python -m ruff check src tests
.venv/bin/python -m ty check
```

## Constraints
- No network calls.
- Inference is best-effort; never fail the build because inference can’t resolve a name.

