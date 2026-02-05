# PROMPT-041: OpenAI Backend (Mocked Tests Only) (L4)

Repo: `/Users/ishitajindal/Documents/jaunt`

## Depends On
- `PROMPT-020` (`jaunt.config` for prompt override paths and LLM config)
- `PROMPT-040` (`jaunt.generate.base`, prompt template files)

## Objective
Implement an OpenAI-backed `GeneratorBackend` that:
- loads prompt templates from packaged defaults (and optional config overrides)
- renders prompts via simple `{{placeholder}}` substitution (no Jinja2)
- calls OpenAI asynchronously
- strips markdown fences if present
- never makes network calls in tests (use mocks)

## Owned Files (avoid editing anything else)
- `src/jaunt/generate/openai_backend.py`
- `tests/test_openai_backend.py`

## Deliverables

### `src/jaunt/generate/openai_backend.py`
Implement:

- `OpenAIBackend` class implementing `GeneratorBackend`
  - `__init__(self, llm: LLMConfig, prompts: PromptsConfig | None = None)`
    - read API key from `os.environ[llm.api_key_env]`
    - store model name
    - create an async OpenAI client (use the official `openai` python package)

  - prompt loading:
    - default templates from packaged resources under `jaunt.prompts/`
    - optional overrides from `PromptsConfig` fields if non-empty:
      - if config provides a path, read that file instead

  - rendering:
    - implement a tiny `render_template(text: str, mapping: dict[str, str]) -> str`
    - placeholders to support (match TASK-040):
      - `spec_module`, `expected_names`, `specs_block`, `deps_api_block`, `deps_generated_block`, `error_context_block`

  - `generate_module(self, ctx: ModuleSpecContext, *, extra_error_context: list[str] | None = None) -> str`
    - choose build vs test templates based on `ctx.kind`
    - render system + module prompts
    - call OpenAI and return text output
    - enforce “code only”:
      - if output contains fenced markdown (```python ... ```), strip fences
      - strip leading/trailing whitespace

Implementation hint (to keep tests stable across OpenAI SDK changes):
- Put the OpenAI call behind a small method, e.g. `_call_openai(messages) -> str`, so tests can patch that method rather than patching deep SDK internals.

## Tests

### `tests/test_openai_backend.py`
No network calls:
- monkeypatch API key env var
- patch the backend’s `_call_openai(...)` (or equivalent) to return:
  - fenced code output and verify fences are stripped
  - unfenced code output
- verify prompt rendering includes expected names
- verify build prompts include an instruction to not generate tests; test prompts include instruction to generate tests

Avoid `pytest-asyncio`; use `asyncio.run(...)` in tests.

## Quality Gates
```bash
.venv/bin/python -m pytest -q tests/test_openai_backend.py
.venv/bin/python -m ruff check src tests
.venv/bin/python -m ty check
```

## Constraints
- No network calls in tests.
- Backend should remain usable without forcing the rest of the system to import OpenAI on startup (import inside backend module is fine).

