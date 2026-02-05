# PROMPT-010C: Runtime API — `@magic` / `@test` (L2)

Repo: `/Users/ishitajindal/Documents/jaunt`

## Depends On
- `PROMPT-010A` (`jaunt.errors`, `jaunt.spec_ref`)
- `PROMPT-010B` (`jaunt.registry`)

## Objective
Implement the public runtime decorators:
- `jaunt.runtime.magic`
- `jaunt.runtime.test`

The key idea: decorators **register** specs at import time, and runtime wrappers/placeholder objects raise helpful errors when code hasn’t been generated.

Tests must be fast and deterministic (mock imports; no real generated files).

## Owned Files (avoid editing anything else)
- `src/jaunt/runtime.py`
- `tests/test_magic_decorator.py`
- `tests/test_test_decorator.py`

Optional (only if you can do it without conflicting with other prompts):
- `src/jaunt/__init__.py` (export `magic`, `test`, exceptions; keep `__version__`; you may keep `hello()` temporarily)

## Deliverables

### `src/jaunt/runtime.py`
Implement:

#### `magic(*, deps=None, prompt=None, infer_deps=None)`
Behavior:
- Only supports **top-level** functions/classes.
  - Reject if `"<locals>" in __qualname__` or `"." in __qualname__` (raise `JauntError`).
- Register a `SpecEntry(kind="magic", ...)` into the registry.
  - `decorator_kwargs` should include keys for `deps`, `prompt`, `infer_deps` when provided.

Functions:
- Return a wrapper callable (use `functools.wraps`).
- On call, attempt to import the generated module and forward the call to the generated function.
- If generated module/function missing: raise `JauntNotBuiltError` with an actionable message mentioning `jaunt build`.

Classes (MVP: import-time substitution, no proxies):
- Reject unsupported custom metaclasses (metaclass != `type`) by raising `JauntError`.
- At decoration time:
  - attempt to import generated module and fetch class by name
  - if found:
    - set `__jaunt_spec_ref__ = "<spec module>:<Qualname>"`
    - rewrite `__module__` to the spec module (avoid leaking `.__generated__` in repr/pickling)
    - return the generated class object
  - else: return a placeholder class that raises `JauntNotBuiltError` on instantiation

#### `test(*, deps=None, prompt=None, infer_deps=None)`
Behavior:
- Register `SpecEntry(kind="test", ...)`.
- Set `fn.__test__ = False` so pytest won’t collect stub specs.
- Return the original function unchanged (no wrapper).

Implementation notes:
- Use `importlib.import_module`.
- Hard-code generated module mapping to `__generated__` for now. Tests should not depend on the exact mapping; they can mock `import_module` to raise `ModuleNotFoundError`.

## Tests

### `tests/test_magic_decorator.py`
Cover:
- registers a function spec and a class spec
- calling an unbuilt function raises `JauntNotBuiltError` with `jaunt build` in the message
- instantiating an unbuilt class raises `JauntNotBuiltError`
- wrapper preserves metadata (name and/or `__wrapped__`)
- decorator stores explicit deps/prompt/string deps in `decorator_kwargs`

### `tests/test_test_decorator.py`
Cover:
- registers test spec
- sets `__test__ = False`
- returns callable unchanged (still callable)
- test specs do not leak into magic registry
- stores deps in `decorator_kwargs`

No filesystem I/O; registry state should be isolated with fixtures calling `clear_registries()`.

## Quality Gates
```bash
.venv/bin/python -m pytest -q tests/test_magic_decorator.py tests/test_test_decorator.py
.venv/bin/python -m ruff check src tests
.venv/bin/python -m ty check
```

## Constraints
- No network calls.
- No writes to any `__generated__/` directory (runtime must not generate).

