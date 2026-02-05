# PROMPT-040: Generation Core — Validation + Retry Wrapper + Prompt Templates (L4)

Repo: `/Users/ishitajindal/Documents/jaunt`

## Depends On
- `PROMPT-010A` (errors, spec_ref types)

## Objective
Implement:
- generated-source validation helpers (`jaunt.validation`)
- generator backend interface + retry-with-error-context wrapper (`jaunt.generate.base`)
- packaged prompt templates (files under `src/jaunt/prompts/`)

No OpenAI calls here; OpenAI backend is a separate prompt.

## Owned Files (avoid editing anything else)
- `src/jaunt/validation.py`
- `src/jaunt/generate/base.py`
- `src/jaunt/prompts/build_system.md`
- `src/jaunt/prompts/build_module.md`
- `src/jaunt/prompts/test_system.md`
- `src/jaunt/prompts/test_module.md`
- `tests/test_validation.py`
- `tests/test_generate_retry.py`

## Deliverables

### `src/jaunt/validation.py`
Implement:
- `validate_generated_source(source: str, expected_names: list[str]) -> list[str]`
  - parse syntax errors via `ast.parse`
  - detect missing **top-level** names:
    - function defs, class defs, and simple assignments (e.g. `CONSTANT = 1`)
  - return a list of human-readable error strings (empty list means “ok”)

- `compile_check(source: str, filename: str) -> list[str]`
  - attempt `compile(source, filename, "exec")`
  - return list of errors (empty = ok)

### `src/jaunt/generate/base.py`
Implement:

- `ModuleSpecContext` dataclass (per TASK-040):
  - `kind: Literal["build","test"]`
  - `spec_module: str`
  - `generated_module: str`
  - `expected_names: list[str]`
  - `spec_sources: dict[SpecRef, str]`
  - `decorator_prompts: dict[SpecRef, str]`
  - `dependency_apis: dict[SpecRef, str]`
  - `dependency_generated_modules: dict[str, str]`

- `GenerationResult` dataclass:
  - `attempts: int`
  - `source: str | None`
  - `errors: list[str]`

- `GeneratorBackend` Protocol / ABC with:
  - `async generate_module(self, ctx: ModuleSpecContext, *, extra_error_context: list[str] | None = None) -> str`
  - `async generate_with_retry(self, ctx: ModuleSpecContext, *, max_attempts: int = 2) -> GenerationResult`
    - call `generate_module`
    - validate output (`validate_generated_source`)
    - retry once with appended “previous output errors: …” as `extra_error_context`

### Prompt template files
Create minimal, strict templates:
- MUST demand “Python code only” output (no markdown fences).
- MUST list required symbol names.
- MUST state the tool writes generated output only (never edit user files).
- `build_*` templates: must not generate tests.
- `test_*` templates: must generate pytest tests (and must not generate src impl).

No need for perfect prompt craft; keep them short and enforce constraints.

## Tests

### `tests/test_validation.py`
Cover:
- valid source with expected names passes
- missing names produce error list mentioning the missing symbol
- syntax errors produce error list mentioning syntax
- class names and assignment names count as defined
- empty expected_names with empty source returns ok

### `tests/test_generate_retry.py`
Create a dummy backend:
- attempt 1 returns invalid python or missing expected symbol
- attempt 2 returns valid python defining expected names
Assertions:
- `generate_with_retry` calls `generate_module` twice
- returns `GenerationResult(attempts=2, source=..., errors=[])`

Avoid `pytest-asyncio`; use `asyncio.run(...)` inside tests.

## Quality Gates
```bash
.venv/bin/python -m pytest -q tests/test_validation.py tests/test_generate_retry.py
.venv/bin/python -m ruff check src tests
.venv/bin/python -m ty check
```

## Constraints
- No network calls.
- Keep retry behavior deterministic (max_attempts default 2).

