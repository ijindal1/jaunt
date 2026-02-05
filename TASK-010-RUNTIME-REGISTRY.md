# TASK-010: Runtime API + Registry (Layer 2 runtime surface)

## Objective
Implement the public runtime decorators `@jaunt.magic` and `@jaunt.test`, plus supporting types:
- exception hierarchy
- stable spec identity (`SpecRef`)
- registries storing discovered specs

This task should not implement CLI/build orchestration or any LLM backend calls.

## Key Decisions (MVP)
- Only supports **top-level** functions and classes as specs (no methods, no nested defs).
- Class handling: **import-time substitution**, no proxy classes.
- Generated module name is hard-coded as `__generated__` (configurable later).
- `SpecRef` must remain stable even if returned object is a generated impl:
  - honor `obj.__jaunt_spec_ref__` if present.

## Deliverables
### Code
- `src/jaunt/errors.py`
  - `JauntError`, `JauntConfigError`, `JauntDiscoveryError`, `JauntNotBuiltError`,
    `JauntGenerationError`, `JauntDependencyCycleError`

- `src/jaunt/spec_ref.py`
  - `SpecRef = NewType("SpecRef", str)`
  - `normalize_spec_ref(s: str) -> SpecRef`
    - accept `"pkg.mod:Qual"` (pass-through)
    - accept shorthand `"pkg.mod.Qual"` (convert to `"pkg.mod:Qual"`)
  - `spec_ref_from_object(obj: object) -> SpecRef`
    - if `hasattr(obj, "__jaunt_spec_ref__")`: use that
    - else: `f"{obj.__module__}:{obj.__qualname__}"`

- `src/jaunt/registry.py`
  - `SpecEntry` dataclass:
    - `kind: Literal["magic","test"]`
    - `spec_ref: SpecRef`
    - `module: str`
    - `qualname: str`
    - `source_file: str`
    - `obj: object` (the decorated object or the user stub object)
    - `decorator_kwargs: dict[str, object]` (deps/prompt/infer_deps)
  - registries + helpers:
    - `register_magic(entry)`, `register_test(entry)`
    - `get_magic_registry()`, `get_test_registry()`
    - `clear_registries()` (for tests)
    - `get_specs_by_module(kind) -> dict[str, list[SpecEntry]]`

- `src/jaunt/runtime.py`
  - `magic(*, deps=None, prompt=None, infer_deps=None)`
    - validate top-level (reject `.` in qualname or `"<locals>"`)
    - register `SpecEntry` into registry
    - functions: return wrapper that imports generated module on call and forwards
    - classes: import-time substitution:
      - if metaclass != type: raise `JauntError` (unsupported in MVP)
      - try to import generated module and fetch class by name
      - if found: set `__jaunt_spec_ref__` and rewrite `__module__` then return it
      - else: return placeholder class raising `JauntNotBuiltError` on instantiation
  - `test(*, deps=None, prompt=None, infer_deps=None)`
    - register
    - set `fn.__test__ = False`
    - return fn unchanged

- Update `src/jaunt/__init__.py`
  - export `magic`, `test`, exceptions, and keep `__version__`

### Tests
Add unit tests under `tests/`:
- SpecRef normalization and `spec_ref_from_object` uses `__jaunt_spec_ref__` override.
- Registry register/get/clear and group-by-module.
- `@test` sets `__test__ = False` and returns original callable.
- `@magic` (functions) raises `JauntNotBuiltError` if generated module missing (mock `importlib.import_module`).
- `@magic` (classes) placeholder instantiation raises `JauntNotBuiltError` when generated class missing.

## Copy/Paste Prompt (for a separate coding agent)
You are implementing TASK-010 in the repo at `/Users/ishitajindal/Documents/jaunt`.

Do:
- Implement `src/jaunt/errors.py`, `src/jaunt/spec_ref.py`, `src/jaunt/registry.py`, `src/jaunt/runtime.py`.
- Update `src/jaunt/__init__.py` to export the runtime API.
- Add/adjust tests under `tests/` for the behaviors described above.

Constraints:
- No CLI work, no backend work, no network calls.
- Keep everything Python 3.12.
- Do not write anything under `__generated__/` in this repo (that’s for user projects).

Quality gates:
- `uv run ruff check .`
- `uv run ty check`
- `uv run pytest`

