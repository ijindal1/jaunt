# PROMPT-050: Build/Test Orchestration (Scheduler + Staleness + Atomic Writes) (L5)

Repo: `/Users/ishitajindal/Documents/jaunt`

## Depends On
- `PROMPT-010A` (errors)
- `PROMPT-010B` (registry types)
- `PROMPT-020` (header + paths)
- `PROMPT-030` (deps + digests)
- `PROMPT-040` (generation core)

OpenAI backend is NOT required for tests; use a FakeBackend returning deterministic code.

## Objective
Implement:
- `jaunt.builder`:
  - staleness detection from module digests vs generated file headers
  - rebuild expansion (dependents of stale modules become stale)
  - async parallel scheduler with topo ordering
  - atomic writes into `__generated__`
- `jaunt.tester`:
  - generate test modules into tests `__generated__`
  - run pytest on explicit generated file paths
  - never write into src tree

## Owned Files (avoid editing anything else)
- `src/jaunt/builder.py`
- `src/jaunt/tester.py`
- `tests/test_builder_io.py`
- `tests/test_build_scheduler.py`
- `tests/test_pytest_runner.py`
- `tests/test_tester_orchestration.py`

## Deliverables

### `src/jaunt/builder.py`
Implement core APIs (names are flexible but tests should use these stable entry points):

- `write_generated_module(...) -> Path`
  - inputs:
    - `package_dir: Path` (root that contains the package directory tree, e.g. `<root>/src`)
    - `generated_dir: str` (usually `"__generated__"`)
    - `module_name: str` (spec module name like `pkg.sub.mod` or `pkg` for package init)
    - `source: str` (generated python code, WITHOUT header)
    - `header_fields: dict[str, object]` compatible with `format_header(...)`
  - behavior:
    - compute generated module relpath via `paths.spec_module_to_generated_module` + `paths.generated_module_to_relpath`
    - ensure directories exist
    - ensure all `__init__.py` files exist along the generated package path
    - write atomically:
      - write to temp file in same dir, then `os.replace`
    - prepend formatted header + blank line before source
    - return final path

- `detect_stale_modules(...) -> set[str]`
  - compare computed module digests (from `digest.module_digest`) vs `header.extract_module_digest` from existing generated file
  - if generated file missing: stale
  - if `force=True`: everything stale

- `run_build(...) -> BuildReport` (async)
  - schedule generation for modules in `stale_modules`, respecting module DAG deps-first
  - concurrency limited by `jobs`
  - priority: prefer critical-path-first (approx ok; can be “longest remaining path length”)
  - for each module:
    - build `ModuleSpecContext`:
      - `expected_names = [e.qualname for e in module_specs]`
      - `spec_sources = {e.spec_ref: extract_source_segment(e) for e in module_specs}`
      - `decorator_prompts` can be `{e.spec_ref: str(e.decorator_kwargs.get("prompt","")) for e in module_specs if e.decorator_kwargs.get("prompt")}`
      - dependency fields can be empty for MVP tests (FakeBackend won’t need them)
    - call `backend.generate_with_retry(ctx)`
    - validate final output (syntax + expected names)
    - write atomically via `write_generated_module`
  - report should include at least:
    - `generated: set[str]`
    - `skipped: set[str]`
    - `failed: dict[str, list[str]]` (module → errors)

### `src/jaunt/tester.py`
Implement the same orchestration pattern as `builder`, but for test modules.

- `run_pytest(files: list[Path], *, pytest_args: list[str]) -> int`
  - execute pytest via subprocess:
    - `[sys.executable, "-m", "pytest", *pytest_args, *files]`
  - return exit code

Also implement (names are flexible; keep them stable for tests):
- `run_test_generation(...) -> TestGenerationReport` (async)
  - input shape can mirror `builder.run_build`:
    - module specs for test modules, spec graph, module dag, stale modules, backend, jobs, project/package dir, generated_dir
  - writes ONLY under `tests/__generated__/...` inside the provided project dir
  - validates generated test modules (syntax + expected names)
  - returns a report with `generated/skipped/failed` sets

- `run_tests(...) -> PytestResult` (async or sync)
  - generates stale tests (unless `no_generate`)
  - runs pytest on explicit generated file paths (unless `no_run`)
  - returns a structured result:
    - `exit_code: int`
    - `passed: bool`
    - `failed: bool`
    - optional `failures: list[str]` (can be empty MVP)

## Tests

### `tests/test_builder_io.py`
Based on the TDD plan, verify:
- writing creates file, includes header + code
- intermediate `__init__.py` exists for generated package path
- atomic overwrite behavior (write twice; final content matches last write)
- `detect_stale_modules` returns stale when missing file
- `force=True` returns everything stale

Use tmp dirs; do not write into repo `src/` or `tests/`.

### `tests/test_build_scheduler.py`
Use a FakeBackend implementing `GeneratorBackend`:
- returns deterministic code defining all expected names
- record call order to assert dep ordering
Tests:
- all stale modules get generated
- dependency order respected when `jobs=1`
- non-stale modules are skipped (backend call_count stays 0)

Avoid `pytest-asyncio`; use `asyncio.run(...)`.

### `tests/test_pytest_runner.py`
Use subprocess-driven pytest on temporary test files:
- passing file returns 0
- failing file returns non-zero
- multiple files pass
- empty file list returns 0 or 5 (no tests collected)

### `tests/test_tester_orchestration.py`
Integration-style but still fast (tmp dirs + FakeBackend):
- create a tmp project with:
  - `src/` and `tests/` directories
  - minimal test spec module entries for something like `tests.test_mod:test_something`
- FakeBackend generates a passing pytest file defining the expected test symbol
- run tester generation and assert:
  - generated file exists under `tests/__generated__/...`
  - no files are written under `src/__generated__/...` (safety)
- run pytest on the generated file via `run_pytest` and assert exit code is 0

## Quality Gates
```bash
.venv/bin/python -m pytest -q tests/test_builder_io.py tests/test_build_scheduler.py tests/test_pytest_runner.py tests/test_tester_orchestration.py
.venv/bin/python -m ruff check src tests
.venv/bin/python -m ty check
```

## Hard Constraints
- Builder writes **only** under `__generated__` within the given `package_dir`.
- Tester writes **only** under tests `__generated__`.
- Never edit user-authored spec modules.
- No network calls in tests.
