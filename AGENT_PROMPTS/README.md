# Jaunt Parallel Agent Prompts

These prompts are derived from:
- `/Users/ishitajindal/Documents/jaunt/jaunt_tdd_plan.md` (ideas / test-first outline)
- `/Users/ishitajindal/Documents/jaunt/TASK-0*.md` (the current MVP architecture spec)

They are written to be **parallel-agent-friendly**:
- each prompt “owns” a small set of files to minimize merge conflicts
- prompts include **dependencies** and **quality gates**
- tests stay **self-contained + fast** (no real LLM calls; use mocks and FakeBackends)

## Quick Review: What To Fix From `jaunt_tdd_plan.md`

The TDD plan is solid in spirit, but several parts don’t match the current TASK specs and/or will fail with the repo as-is:

- **Missing “discovery” task:** the plan has `jaunt/discovery.py` (`discover_modules`, `import_and_collect`), but there is no `TASK-*` for it. The CLI needs discovery, so I split it into its own prompt.
- **Module path mismatches:** the plan uses `jaunt/base.py` and `jaunt/openai_backend.py`, but `TASK-040` specifies `src/jaunt/generate/base.py` and `src/jaunt/generate/openai_backend.py`.
- **API name mismatches:** registry/deps/validation functions in the plan use names that differ from `TASK-*` (e.g. `build_dependency_graph` vs `build_spec_graph`, `compile_check -> bool` vs `compile_check -> list[str]`).
- **Async tests need a strategy:** the plan uses `pytest.mark.asyncio`, which requires `pytest-asyncio` (or rewrite async tests to use `asyncio.run`).
- **`pyproject.toml` assumptions:** the plan expects an `openai` dependency; current `pyproject.toml` has none. Decide if OpenAI is a hard dependency (MVP: yes) or optional extra (more work).
- **`uv` not on PATH in this environment:** local quality gates work via the existing venv:
  - `.venv/bin/python -m pytest -q`
  - `.venv/bin/python -m ruff check .`
  - `.venv/bin/python -m ty check`

The prompts below assume the **TASK-* docs are canonical**, and adjust the test plan accordingly.

## Prompts (Suggested Parallelization)

Can start immediately (minimal dependencies):
- `PROMPT-010A-FOUNDATIONS-ERRORS-SPECREF.md`
- `PROMPT-020-CONFIG-HEADER-PATHS.md`
- `PROMPT-070-SKILL-DOCS.md`
- `PROMPT-090-PACKAGING-DEPS.md`

After `PROMPT-010A` (needs `jaunt.errors` / `jaunt.spec_ref`):
- `PROMPT-010B-REGISTRY.md`
- `PROMPT-025-DISCOVERY.md`

After `PROMPT-010B` (needs `SpecEntry` + registries):
- `PROMPT-010C-RUNTIME-DECORATORS.md`
- `PROMPT-030-DEPS-DIGESTS.md`

After `PROMPT-010C`:
- `PROMPT-015-PUBLIC-API-EXPORTS.md`

After `PROMPT-010A`:
- `PROMPT-040-GENERATION-CORE.md`

After `PROMPT-020` + `PROMPT-040` (+ `PROMPT-090` if OpenAI is required):
- `PROMPT-041-OPENAI-BACKEND.md`

After `PROMPT-020` + `PROMPT-030` + `PROMPT-040`:
- `PROMPT-050-BUILD-TEST-ORCHESTRATION.md`

After `PROMPT-025` + `PROMPT-050`:
- `PROMPT-060-CLI.md`

Late-stage:
- `PROMPT-080-INTEGRATION-TESTS.md`

## Design Intent (From `jaunt_tdd_plan.md`)

Key choices preserved in these prompts:
- Tests should be **self-contained and fast**. No real LLM calls; OpenAI backend tests are mocked.
- The “test dependency map” idea is the guide: you should be able to write/run green tests as soon as the prior layers exist.
- MVP tests are intentionally shallow: correctness first, then add stress/edge cases when things break.
- Integration test starts as a skeleton; the full build+test cycle is the “victory lap” once all layers exist.

## House Rules For Parallel Agents

- Only edit the “Owned files” listed in your prompt, unless the prompt explicitly says otherwise.
- Prefer importing modules directly in tests (e.g. `from jaunt.errors import ...`) to avoid conflicts in `src/jaunt/__init__.py`.
- No network calls in tests.
- Never write anything into a user’s `__generated__/` tree except inside tmp dirs in tests.
