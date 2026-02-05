# TASK-040: Layer 1 Generation Backends (Prompts + Retry + OpenAI)

## Objective
Implement the Layer 1 code generation subsystem that turns a prepared `ModuleSpecContext` into Python source code.

This task owns:
- prompt templates stored as files (not hard-coded f-strings)
- backend interface
- OpenAI backend implementation
- retry-with-error-context wrapper
- validation helpers (syntax + required names)

This task should not implement dependency graphs, digests, discovery, or CLI orchestration.

## Key Decisions (MVP)
- Prompt templates shipped as package resources:
  - `src/jaunt/prompts/build_system.md`
  - `src/jaunt/prompts/build_module.md`
  - `src/jaunt/prompts/test_system.md`
  - `src/jaunt/prompts/test_module.md`
- Templates use simple `{{placeholder}}` substitution (no Jinja2 dependency in MVP).
- Backends do **2 attempts** by default:
  - attempt 2 appends “previous output errors: …” to the prompt.

## Deliverables
### Code
- `src/jaunt/validation.py`
  - `validate_generated_source(source: str, expected_names: list[str]) -> list[str]`
    - syntax parse errors
    - missing top-level definitions
  - `compile_check(source: str, filename: str) -> list[str]`
    - return list of errors (empty = ok)

- `src/jaunt/generate/base.py`
  - `ModuleSpecContext` dataclass:
    - `kind: Literal["build","test"]`
    - `spec_module: str` (source module name)
    - `generated_module: str`
    - `expected_names: list[str]`
    - `spec_sources: dict[SpecRef, str]` (source segments for each spec)
    - `decorator_prompts: dict[SpecRef, str]` (optional extra prompt per spec)
    - `dependency_apis: dict[SpecRef, str]` (signature + docstring for deps)
    - `dependency_generated_modules: dict[str, str]` (module name -> generated source if available)
  - `GenerationResult` dataclass:
    - `attempts: int`
    - `source: str | None`
    - `errors: list[str]`
  - `GeneratorBackend` ABC/Protocol:
    - `async generate_module(self, ctx: ModuleSpecContext, *, extra_error_context: list[str] | None = None) -> str`
    - `async generate_with_retry(self, ctx: ModuleSpecContext, *, max_attempts: int = 2) -> GenerationResult`
      - calls `generate_module`, validates output, retries once with error-context

- `src/jaunt/generate/openai_backend.py`
  - Use OpenAI API (async client).
  - Read API key from env var named by config (`llm.api_key_env`).
  - Load prompt templates from:
    - packaged defaults (importlib.resources)
    - optional overrides from config `[prompts]` (file paths)
  - Construct prompt by rendering templates with placeholders:
    - `{{spec_module}}`, `{{expected_names}}`, `{{specs_block}}`, `{{deps_api_block}}`,
      `{{deps_generated_block}}`, `{{error_context_block}}`
  - Must enforce output is **Python code only**:
    - strip markdown fences if present
  - Builder prompt MUST NOT generate tests; tester prompt MUST NOT generate src impl.

### Prompt Files
Add under `src/jaunt/prompts/`:
- `build_system.md`
- `build_module.md`
- `test_system.md`
- `test_module.md`

Prompts must:
- demand code-only output
- list required symbol names and signatures
- state “do not edit user files; only emit generated module source”

### Tests
Under `tests/`:
- validation catches syntax errors and missing expected defs
- `generate_with_retry` calls backend twice when validation fails (use a dummy backend that returns bad then good code)
- prompt rendering loads packaged defaults (no OpenAI calls)

## Copy/Paste Prompt (for a separate coding agent)
You are implementing TASK-040 in the repo at `/Users/ishitajindal/Documents/jaunt`.

Do:
- Implement `src/jaunt/validation.py`, `src/jaunt/generate/base.py`, `src/jaunt/generate/openai_backend.py`.
- Add prompt template files under `src/jaunt/prompts/`.
- Add tests for validation + retry wrapper + template loading (no network calls).

Constraints:
- Do not call OpenAI in tests.
- Keep runtime dependencies minimal; no Jinja2 in MVP.

Quality gates:
- `uv run ruff check .`
- `uv run ty check`
- `uv run pytest`

