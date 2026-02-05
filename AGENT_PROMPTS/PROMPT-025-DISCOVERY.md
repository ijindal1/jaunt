# PROMPT-025: Discovery — Module Scanning + Import Collection (L2)

Repo: `/Users/ishitajindal/Documents/jaunt`

## Depends On
- `PROMPT-010A` (`jaunt.errors`)
- `PROMPT-010B` (`jaunt.registry`) and `PROMPT-010C` (`jaunt.runtime`) will be used by callers, but discovery itself can be implemented without them.

## Objective
Implement:
- filesystem scanning to find Python modules under one or more roots
- importing discovered modules to populate registries (via decorators)

Tests must be fast: use tmp dirs; no network; no generated code.

## Owned Files (avoid editing anything else)
- `src/jaunt/discovery.py`
- `tests/test_discovery.py`

## Deliverables

### `src/jaunt/discovery.py`
Implement:

- `discover_modules(*, roots: list[Path], exclude: list[str], generated_dir: str) -> list[str]`
  - Scan for `*.py` under each root.
  - Convert path → module name:
    - relative to the root
    - strip `.py`
    - replace path separators with `.`
    - `__init__.py` maps to the package module (`pkg/__init__.py` → `pkg`)
  - Exclude:
    - anything under any directory named `generated_dir` (e.g. `__generated__`)
    - anything matching any glob in `exclude` (treat patterns as matching against a posix-style relative path)
  - Return sorted, unique module names.

- `import_and_collect(module_names: list[str], *, kind: Literal["magic","test"]) -> None`
  - Import each module by name (`importlib.import_module`).
  - Any import error (SyntaxError, ImportError, etc) should be wrapped as `JauntDiscoveryError` with the module name in the message.
  - Do not try to be clever with sys.path here; callers (CLI/tests) will set it.

Design notes:
- This module should not know about the generated module mapping or digests.
- Keep `discover_modules` pure-ish: do not mutate sys.path or import modules.

## Tests

### `tests/test_discovery.py`
Use the TDD plan structure but align to the API above.
Cover:
- finds `pkg.foo`, `pkg.bar` given a tmp dir with those files
- excludes `__generated__`
- honors exclude globs like `**/.venv/**`
- returns sorted modules
- import errors get wrapped in `JauntDiscoveryError` and mention the module name

Implementation hint for tests:
- Use `monkeypatch.syspath_prepend(str(tmp_path))` to make tmp packages importable.

## Quality Gates
```bash
.venv/bin/python -m pytest -q tests/test_discovery.py
.venv/bin/python -m ruff check src tests
.venv/bin/python -m ty check
```

## Constraints
- No network calls.
- Keep scanning fast; avoid quadratic path operations.

