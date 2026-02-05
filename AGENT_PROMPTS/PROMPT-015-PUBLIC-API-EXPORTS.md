# PROMPT-015: Public API Exports (`jaunt.__init__`) + Scaffold Cleanup

Repo: `/Users/ishitajindal/Documents/jaunt`

## Depends On
- `PROMPT-010A` (errors)
- `PROMPT-010C` (runtime decorators)

## Objective
Make `import jaunt` expose the intended MVP public API:
- `jaunt.magic`, `jaunt.test`
- all Jaunt exception types
- `jaunt.__version__`

Optionally remove the initial scaffolded `hello()` API/tests so the package surface matches the MVP plan.

## Owned Files (avoid editing anything else)
- `src/jaunt/__init__.py`
- `tests/test_basic.py`
- (optional) add `tests/test_public_api.py`

## Deliverables

### `src/jaunt/__init__.py`
Update exports:
- keep `__version__` logic (source checkout fallback ok)
- export:
  - `magic`, `test`
  - `JauntError`, `JauntConfigError`, `JauntDiscoveryError`, `JauntNotBuiltError`, `JauntGenerationError`, `JauntDependencyCycleError`
- set `__all__` accordingly

Optional cleanup:
- remove `hello()` if you want a clean surface; if you remove it, update tests accordingly.

## Tests

Update `tests/test_basic.py` (or replace with `tests/test_public_api.py`) to assert:
- `jaunt.__version__` is a string
- `callable(jaunt.magic)` and `callable(jaunt.test)`
- exception classes are importable from `jaunt` and are subclasses of `Exception`

Do not add slow subprocess tests here; keep it pure import-level checks.

## Quality Gates
```bash
.venv/bin/python -m pytest -q tests/test_basic.py tests/test_public_api.py
.venv/bin/python -m ruff check src tests
.venv/bin/python -m ty check
```

## Constraints
- No network calls.
- Avoid editing CLI files here (owned by the CLI prompt).

