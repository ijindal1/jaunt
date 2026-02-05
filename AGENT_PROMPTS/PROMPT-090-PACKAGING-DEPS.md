# PROMPT-090: Packaging + Dependencies (pyproject / resources)

Repo: `/Users/ishitajindal/Documents/jaunt`

## Depends On
None. This can run in parallel, but be careful: it touches `pyproject.toml` which is a merge hotspot.

## Objective
Make packaging and dependencies match the MVP plan:
- add runtime dependency on `openai` (needed for `OpenAIBackend`)
- ensure package data is included in wheels:
  - `src/jaunt/prompts/*.md`
  - `src/jaunt/skill/**`
- keep dev tooling stable (pytest, ruff, ty)

## Owned Files (avoid editing anything else)
- `pyproject.toml`

Optional (only if you have `uv` available and want to keep lock in sync):
- `uv.lock`

## Deliverables

### `pyproject.toml`
Update:
- `[project].dependencies` includes the OpenAI python SDK (pick a conservative lower bound; e.g. `openai>=1.0.0`).
- Add Hatchling include rules so prompt templates + skill docs are packaged.
  - Example approach:
    - `tool.hatch.build.targets.wheel.include = ["src/jaunt/prompts/**", "src/jaunt/skill/**", "src/jaunt/py.typed"]`
  - Ensure markdown files are included.

Do not add extra dependencies unless required.

## Tests / Verification
In this environment, `uv` is not on PATH, but `.venv` exists.
Verify at least:
```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ty check
```

If you update `uv.lock`, also verify the lock step you used is reproducible.

## Constraints
- No behavior changes outside of dependency/packaging.
- Keep `requires-python = ">=3.12"`.

