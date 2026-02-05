# PROMPT-010A: Foundations — Errors + SpecRef (L0)

You are implementing the earliest Jaunt MVP foundation modules. Keep tests **self-contained, fast, and deterministic**.

Repo: `/Users/ishitajindal/Documents/jaunt`

## Objective
Implement:
- the Jaunt exception hierarchy (`jaunt.errors`)
- stable spec identity helpers (`jaunt.spec_ref`)

This prompt is intentionally independent so other agents can run in parallel.

## Owned Files (avoid editing anything else)
- `src/jaunt/errors.py`
- `src/jaunt/spec_ref.py`
- `tests/test_errors.py`
- `tests/test_spec_ref.py`

## Deliverables

### `src/jaunt/errors.py`
Implement:
- `class JauntError(Exception)`
- `class JauntConfigError(JauntError)`
- `class JauntDiscoveryError(JauntError)`
- `class JauntNotBuiltError(JauntError)`
- `class JauntGenerationError(JauntError)`
- `class JauntDependencyCycleError(JauntError)`

### `src/jaunt/spec_ref.py`
Implement:
- `SpecRef = NewType("SpecRef", str)`
- `normalize_spec_ref(s: str) -> SpecRef`
  - Accept canonical `"pkg.mod:Qualname"` unchanged.
  - Accept shorthand `"pkg.mod.Qualname"` and convert to `"pkg.mod:Qualname"`.
  - Allow qualnames with dots when colon-form is used: `"pkg.mod:Outer.Inner"` stays as-is.
  - Validate minimal sanity (non-empty module + qualname); raise `ValueError` for obviously invalid inputs.
- `spec_ref_from_object(obj: object) -> SpecRef`
  - If `obj.__jaunt_spec_ref__` exists, use that (string, normalized).
  - Else derive `f"{obj.__module__}:{obj.__qualname__}"`.

## Tests

### `tests/test_errors.py`
Create tests similar to the TDD plan:
- subclass relationships (all are `JauntError`)
- messages preserved
- can catch any Jaunt error via `except JauntError`

### `tests/test_spec_ref.py`
Create tests:
- normalize colon format pass-through
- normalize dot shorthand conversion
- nested qualname stability for colon-form
- `spec_ref_from_object` for function and class
- `__jaunt_spec_ref__` override is honored

Keep tests shallow and pure (no filesystem needed here).

## Quality Gates
Run using the existing venv (this repo currently does not have `uv` on PATH):
```bash
.venv/bin/python -m pytest -q tests/test_errors.py tests/test_spec_ref.py
.venv/bin/python -m ruff check src tests
.venv/bin/python -m ty check
```

## Notes / Constraints
- Python >= 3.12.
- No network calls.
- Keep the public surface small; don’t add extra dependencies.

