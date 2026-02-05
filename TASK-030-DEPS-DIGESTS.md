# TASK-030: Dependency Graph + Digests (Incremental rebuild core)

## Objective
Implement:
- spec-level dependency graph from explicit deps + optional best-effort inference
- module DAG collapse + topo sort + cycle errors
- stable digests to drive incremental rebuild of generated modules

This task should not implement CLI scheduling or LLM backends.

## Inputs
From registry (`SpecEntry`):
- `spec_ref` (`"{module}:{qualname}"`)
- `module`, `qualname`
- `source_file`
- `decorator_kwargs["deps"]` (objects or strings)
- `decorator_kwargs["infer_deps"]` (optional override)

## Deliverables
### Code
- `src/jaunt/deps.py`
  - `build_spec_graph(specs: dict[SpecRef, SpecEntry], *, infer_default: bool) -> dict[SpecRef, set[SpecRef]]`
    - explicit deps: normalize to SpecRefs; ignore missing deps with warning hook (do not crash MVP)
    - inference (best-effort, optional):
      - parse module AST once; build alias map for `import x as a` and `from x import y as b`
      - for a given top-level def/class body, collect Name + simple Attribute roots used
      - resolve to known SpecRefs in the loaded spec set; add edges
  - `collapse_to_module_dag(spec_graph) -> dict[str, set[str]]`
  - `toposort(graph) -> list[K]`
    - on cycle: raise `JauntDependencyCycleError` with a cycle path in the message

- `src/jaunt/digest.py`
  - `extract_source_segment(entry: SpecEntry) -> str`
    - read file, `ast.parse`, find top-level def/class by name, return `ast.get_source_segment`
  - `local_digest(entry: SpecEntry) -> str`
    - sha256(normalized source segment + stable JSON of decorator kwargs where deps are converted to SpecRefs)
  - `graph_digest(spec_ref, specs, spec_graph) -> str`
    - recursive memoized sha256(local + sorted(dep graph digests))
  - `module_digest(module_name: str, module_specs: list[SpecEntry], spec_graph) -> str`
    - sha256(sorted(graph_digest(spec) for spec in module_specs))

Normalization rules:
- ensure consistent whitespace handling so digest doesn’t change due to indentation trivia
- stable JSON: sort keys, ensure all values JSON-serializable (convert deps objects -> SpecRefs)

### Tests
Under `tests/`:
- explicit deps build correct edges + valid topo order
- cycle detection raises `JauntDependencyCycleError` with cycle path included
- digest determinism
- digest change propagation: changing a dependency changes dependent graph/module digest

## Copy/Paste Prompt (for a separate coding agent)
You are implementing TASK-030 in the repo at `/Users/ishitajindal/Documents/jaunt`.

Do:
- Implement `src/jaunt/deps.py` and `src/jaunt/digest.py` as specified.
- Add focused unit tests under `tests/`.

Constraints:
- Inference is best-effort; never fail the build solely because inference can’t resolve a name.
- Assume specs are top-level only.
- No CLI/backend work.

Quality gates:
- `uv run ruff check .`
- `uv run ty check`
- `uv run pytest`

