# PROMPT-070: Skill Docs (Layer 3 AI Assistant UX)

Repo: `/Users/ishitajindal/Documents/jaunt`

## Depends On
None (writing + packaging-only). This can run in parallel with code prompts.

## Objective
Create the “Jaunt skill” documentation shipped with the package:
- `SKILL.md` (canonical)
- `cursorrules.md` (Cursor adaptation)
- `examples/` for specs + tests + config

The docs must encode the core philosophy:
- The AI assistant writes **intent** (specs).
- Jaunt generates **implementation** into `__generated__/`.
- Human reviews generated output and iterates.

## Owned Files (avoid editing anything else)
- `src/jaunt/skill/SKILL.md`
- `src/jaunt/skill/cursorrules.md`
- `src/jaunt/skill/examples/basic_function_spec.py`
- `src/jaunt/skill/examples/class_spec.py`
- `src/jaunt/skill/examples/test_spec.py`
- `src/jaunt/skill/examples/jaunt.toml`
- (optional) `tests/test_packaged_resources.py`

## Deliverables

### Docs content requirements (match TASK-070)
`SKILL.md` structure:
1. What is Jaunt (1 paragraph, AI-parseable)
2. Your Role as an AI Assistant
3. Workflow to guide (specs -> build -> review -> iterate)
4. Writing good spec stubs (largest section; include templates)
5. Writing good test specs
6. Config reference (`jaunt.toml`)
7. Critical rules (never edit `__generated__/`, always regenerate via CLI, always review)

`cursorrules.md`:
- same rules but formatted like typical `.cursorrules`

Examples:
- simple `@jaunt.magic` function spec
- class spec with docstrings and invariants
- `@jaunt.test` test spec referencing magic functions
- minimal `jaunt.toml`

### Optional test
`tests/test_packaged_resources.py`:
- smoke-test `importlib.resources` can find the expected skill files
- no wheel build required; just check resources exist in source tree package

## Quality Gates
```bash
.venv/bin/python -m pytest -q tests/test_packaged_resources.py
.venv/bin/python -m ruff check src tests
.venv/bin/python -m ty check
```

## Notes
- Keep docs concise but actionable.
- Assume assistants will follow this as a “skill”; be explicit, imperative, and unambiguous.

