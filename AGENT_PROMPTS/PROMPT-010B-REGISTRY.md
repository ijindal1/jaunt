# PROMPT-010B: Core Data Structures — Registry (L1)

Repo: `/Users/ishitajindal/Documents/jaunt`

## Depends On
- `PROMPT-010A` (`jaunt.errors`, `jaunt.spec_ref`)

## Objective
Implement the global registries that store discovered specs from decorators.

Tests must be self-contained and fast. No filesystem scanning and no imports of user projects in this prompt.

## Owned Files (avoid editing anything else)
- `src/jaunt/registry.py`
- `tests/test_registry.py`

## Deliverables

### `src/jaunt/registry.py`
Implement:

- `SpecEntry` dataclass with fields (MVP):
  - `kind: Literal["magic", "test"]`
  - `spec_ref: SpecRef`
  - `module: str`
  - `qualname: str`
  - `source_file: str`
  - `obj: object`
  - `decorator_kwargs: dict[str, object]`

- Global registries:
  - magic registry: `dict[SpecRef, SpecEntry]`
  - test registry: `dict[SpecRef, SpecEntry]`

- Functions:
  - `register_magic(entry: SpecEntry) -> None`
  - `register_test(entry: SpecEntry) -> None`
  - `get_magic_registry() -> dict[SpecRef, SpecEntry]`
  - `get_test_registry() -> dict[SpecRef, SpecEntry]`
  - `clear_registries() -> None` (for tests)
  - `get_specs_by_module(kind: Literal["magic","test"]) -> dict[str, list[SpecEntry]]`
    - group entries by `entry.module`
    - within a module, keep a stable order (e.g., sort by `qualname` then `spec_ref`)

Design notes:
- Duplicate registrations should overwrite (last write wins). This makes repeated imports / reload stable.
- Avoid surprising global state exposure; returning the dict is fine for MVP but tests should treat as read-only.

## Tests

### `tests/test_registry.py`
Include:
- autouse fixture to clear registries pre/post
- register + retrieve for magic
- register + retrieve for test
- separation between registries
- clear resets both
- group-by-module behavior
- duplicate registration overwrites decorator_kwargs

Don’t rely on real modules; create `SpecEntry` with dummy objects and fake source_file strings.

## Quality Gates
```bash
.venv/bin/python -m pytest -q tests/test_registry.py
.venv/bin/python -m ruff check src tests
.venv/bin/python -m ty check
```

## Constraints
- No network calls.
- Keep everything pure (no I/O).

