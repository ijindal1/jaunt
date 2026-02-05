# Jaunt MVP Plan (Library + CLI + Prompt Templates + Skill Docs)

## Summary
Jaunt is a Python workflow that lets users write **spec stubs** (decorated pseudocode + comments + docstrings) in normal Python modules, and generates real implementations/tests into `__generated__/` without ever editing user-written code.

There are **three AI layers** and they must stay separated:

1. **Layer 1: Builder/Tester backends** (LLM calls)
   - Controlled by Jaunt internal prompts + config.
   - Writes only to generated output trees.
2. **Layer 2: Jaunt CLI** (`jaunt build`, `jaunt test`)
   - Orchestrates discovery, dependency graph, checksums, scheduling.
   - Performs validation, retry with error-context, atomic writes.
3. **Layer 3: User’s AI assistant** (Cursor/Claude/Copilot)
   - Helps humans write *better specs* and review generated output.
   - Should not short-circuit by writing implementations directly.

## MVP Scope
### Must-have
- `@jaunt.magic` for **top-level** functions and classes in user modules.
- `@jaunt.test` for **top-level** test spec functions in user test modules.
- CLI:
  - `jaunt build`: incremental, dependency-aware generation for src, parallelized.
  - `jaunt test`: generate tests + run pytest (optionally runs `build` first).
- Incremental rebuild:
  - compute module digests from the **spec dependency graph**
  - embed digests in generated file headers and skip when unchanged
- Builder/tester separation:
  - builder writes only src `__generated__`
  - tester writes only tests `__generated__`
  - neither ever edits user-written code/specs

### Non-goals (MVP)
- Auto-generation at runtime. Generation is manual CLI-only.
- Proxy/metaclass magic for class dispatch. No attempt to preserve perfect identity semantics beyond import-time substitution.
- Deep cross-module static callgraph inference. Inference is best-effort, shallow, and optional.
- Supporting methods/nested defs as specs.

## User Project Layout (Target)
Example:
```
my-project/
- jaunt.toml
- my_project/
  - __init__.py            # user spec stubs
  - feature.py             # user spec stubs
  - __generated__/         # generated src impl
    - __init__.py
    - feature.py
- tests/
  - __init__.py            # user test specs
  - __generated__/         # generated pytest tests
    - __init__.py
```

Mapping (per-module generation):
- `my_project/foo.py` -> `my_project/__generated__/foo.py`
- `my_project/__init__.py` -> `my_project/__generated__/__init__.py`

## Public API (Python)
- `jaunt.magic(...)`
- `jaunt.test(...)`
- exceptions: `JauntError`, `JauntConfigError`, `JauntDiscoveryError`, `JauntNotBuiltError`,
  `JauntGenerationError`, `JauntDependencyCycleError`

### Spec identity: `SpecRef`
Canonical identity string: `"{module}:{qualname}"` (e.g. `my_project.foo:cowsay_dialog`).
Must be stable even if an object is replaced by a generated implementation:
- If `obj.__jaunt_spec_ref__` exists, use it.

### `@magic` runtime dispatch
#### Functions
- Decorator registers spec in a global registry.
- Returns a wrapper function that imports the generated module at call time and forwards the call.
- If missing: raise `JauntNotBuiltError` with message instructing `jaunt build`.

#### Classes (MVP decision: **import-time substitution**, no proxy)
- Decorator registers spec in registry.
- At decoration time:
  - attempt to import generated module and fetch the class by name
  - if present: return the real generated class object
    - set `__jaunt_spec_ref__ = "<spec module>:<Qualname>"`
    - rewrite `__module__` to the spec module (avoid leaking `.__generated__` in repr/pickling)
  - else: return a placeholder class that raises `JauntNotBuiltError` on instantiation
- Unsupported in MVP: custom metaclasses (metaclass != `type`) -> raise clear error.

### `@test`
- Registers test spec.
- Sets `fn.__test__ = False` so pytest won’t collect the stub.
- Returns function unchanged.

## CLI Commands
Entry point: `jaunt = "jaunt.cli:main"`.

### `jaunt build`
Pipeline:
1. Load `jaunt.toml`.
2. Discover + import source spec modules (import-based registry).
3. Build spec dependency graph from explicit deps + optional inference.
4. Compute per-module digest (SHA-256) based on spec graph digests.
5. Compare to header digest in existing generated file; determine stale modules.
6. Expand rebuild set to include dependents of stale modules.
7. Generate stale modules in parallel, obeying module DAG (topo ordering).
8. Validate generated source (AST parse + required symbol names) and write atomically.

Parallelization detail:
- Limit concurrency by `jobs`.
- When multiple modules are ready, prefer “depth-first” by prioritizing longer remaining path length (critical path first).

### `jaunt test`
Pipeline:
1. By default run `jaunt build` first (`--no-build` disables).
2. Discover + import test spec modules.
3. Generate stale test modules into tests `__generated__/` only.
4. Run pytest by **explicit generated file paths** (avoid collecting spec stubs).
5. Return pytest exit code mapping (see below).

Exit codes:
- `0` success
- `2` config/discovery errors
- `3` generation/validation errors
- `4` pytest failures

## Config: `jaunt.toml`
Read via stdlib `tomllib` (Python 3.12+), root discovered by walking upward for `jaunt.toml`.

Minimum config (example):
```toml
version = 1

[paths]
source_roots = ["src", "."]
test_roots = ["tests"]
generated_dir = "__generated__"

[llm]
provider = "openai"
model = "gpt-5.2"
api_key_env = "OPENAI_API_KEY"

[build]
jobs = 8
infer_deps = true

[test]
jobs = 4
infer_deps = true
pytest_args = ["-q"]

[prompts]
# Optional overrides. If omitted, Jaunt uses packaged defaults.
build_system = ""
build_module = ""
test_system = ""
test_module = ""
```

## Generated File Header
Every generated module begins with:
- `# This file was generated by jaunt. DO NOT EDIT.`
- `# jaunt:tool_version=...`
- `# jaunt:kind=build|test`
- `# jaunt:source_module=...`
- `# jaunt:module_digest=sha256:<hex>`
- `# jaunt:spec_refs=[...]`

Staleness check: parse header, compare `module_digest`.

## Layer 1 Backend Requirements
### Prompt templates live in files
Prompts are shipped as package resources and loaded at runtime:
```
src/jaunt/prompts/
  build_system.md
  build_module.md
  test_system.md
  test_module.md
```
Templates use simple `{{placeholders}}` substitution (no Jinja2 dependency in MVP).

### Retry with error-context (cheap + high ROI)
Backend call flow:
1. attempt 1: generate -> validate
2. if validation fails: attempt 2 with appended “previous output errors: …”
3. if still fails: record failure

## Layer 3 Skill Docs (AI Assistant Guidance)
Ship an AI-assistant “skill” doc set:
```
src/jaunt/skill/
  SKILL.md
  cursorrules.md
  examples/
    basic_function_spec.py
    class_spec.py
    test_spec.py
    jaunt.toml
```
Add a CLI helper:
- `jaunt skill export [--dest PATH]` to write these files into a user project for easy adoption.

## Task Breakdown
This repo should contain the following TASK files for parallel work:
- `TASK-010-RUNTIME-REGISTRY.md`
- `TASK-020-CONFIG-HEADER-PATHS.md`
- `TASK-030-DEPS-DIGESTS.md`
- `TASK-040-GENERATION-BACKENDS.md`
- `TASK-050-BUILD_TEST_ORCHESTRATION.md`
- `TASK-060-CLI.md`
- `TASK-070-SKILL-DOCS.md`

