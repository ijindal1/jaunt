# TASK-050: Layer 2 Build/Test Orchestration (Scheduler + Staleness + Writes)

## Objective
Implement the Layer 2 orchestration logic that:
- determines what needs regeneration (checksums + dependency expansion)
- schedules module generation in parallel topological order (depth-first priority)
- validates and writes generated files atomically

This task should not implement discovery scanning/imports (it consumes registries/module specs) and should not implement the OpenAI backend itself (it consumes `GeneratorBackend`).

## Hard Safety Constraints (MVP)
- Builder writes **only** to src package `__generated__/...`
- Tester writes **only** to tests `__generated__/...`
- Neither ever edits user-written spec modules or user-written test specs

## Deliverables
### Code
- `src/jaunt/builder.py`
  - Compute staleness by comparing computed module digest vs header `module_digest`.
  - Expand rebuild set: if module stale, all dependents are stale.
  - Parallel scheduler:
    - input: `module_dag: dict[str, set[str]]`, `stale_modules: set[str]`
    - enforce deps-before-dependents
    - concurrency `jobs`
    - ready-queue priority = depth-first (critical path first)
  - For each module:
    - build `ModuleSpecContext` (expected names, spec sources, dep APIs, dep generated sources if available)
    - call `backend.generate_with_retry(ctx)`
    - validate final output (syntax + expected names)
    - write atomically to generated path:
      - ensure `__generated__` package dirs exist
      - ensure intermediate `__init__.py` exist as needed
      - prepend formatted header

- `src/jaunt/tester.py`
  - Same orchestration pattern, but output root is tests `__generated__/...`
  - After generation, run pytest by explicit generated file list
  - Return structured result:
    - `PytestResult(exit_code, passed, failed, failures=[...])`
    - MVP can parse failures minimally (e.g. from pytest summary), but define structure now for future feedback loops.

### Tests
Under `tests/` (integration-style with tmp dirs):
- A FakeBackend generates deterministic code for a dummy user project layout.
- `builder`:
  - first run writes generated modules
  - second run skips unchanged modules
  - change a spec -> rebuild module + dependents
  - ensure builder never writes into tests tree
- `tester`:
  - generates tests into tests `__generated__`
  - runs pytest successfully on generated file paths
  - ensure tester never writes into src tree

## Copy/Paste Prompt (for a separate coding agent)
You are implementing TASK-050 in the repo at `/Users/ishitajindal/Documents/jaunt`.

Do:
- Implement `src/jaunt/builder.py` and `src/jaunt/tester.py` as described.
- Add integration tests using `tmp_path` and a FakeBackend.

Constraints:
- Do not depend on OpenAI in tests.
- Enforce the write-safety constraints strictly.

Quality gates:
- `uv run ruff check .`
- `uv run ty check`
- `uv run pytest`

