# PROMPT-080: Integration Tests (“Victory Lap”)

Repo: `/Users/ishitajindal/Documents/jaunt`

## Depends On
This is intentionally last:
- runtime decorators (`PROMPT-010C`) + exports in `jaunt.__init__`
- config (`PROMPT-020`)
- discovery (`PROMPT-025`)
- deps/digests (`PROMPT-030`)
- generation backend (FakeBackend ok; `PROMPT-040`)
- orchestration (`PROMPT-050`)
- CLI (`PROMPT-060`) optional

## Objective
Write an end-to-end-ish integration test file that:
- creates a realistic tmp project structure
- verifies discovery + registry registration works
- optionally (later) runs a full build + test cycle using FakeBackend

Keep the initial integration test shallow, fast, and reliable. It should not require OpenAI.

## Owned Files (avoid editing anything else)
- `tests/test_integration.py`

## Deliverables

### `tests/test_integration.py`
Implement:
- a helper to create a minimal Jaunt project in `tmp_path`:
  - `jaunt.toml`
  - `src/<pkg>/__init__.py` with `@jaunt.magic` stubs
  - `tests/__init__.py` with `@jaunt.test` stubs
- a test that:
  - manipulates `sys.path` to import the tmp project package
  - imports/reloads the package module
  - asserts the magic registry contains the expected spec ref
  - cleans up `sys.path` and `sys.modules` robustly

Optional (guarded / skipped until ready):
- full build cycle test using a FakeBackend wired into `builder.run_build`
- full test cycle invoking `tester.run_pytest` on generated tests

## Quality Gates
```bash
.venv/bin/python -m pytest -q tests/test_integration.py
.venv/bin/python -m ruff check src tests
.venv/bin/python -m ty check
```

## Constraints
- No network calls.
- Keep it under ~1s runtime.

