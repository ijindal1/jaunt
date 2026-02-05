# uv Command Notes (Quick Reference)

Prefer verifying exact flags with:
- `uv --help`
- `uv pip --help`
- `uv venv --help`

## Common Patterns

Virtual environment:
- Create venv: `uv venv` (optionally `--python X.Y`)

Pip-compatible dependency management:
- Install from requirements: `uv pip install -r requirements.txt`
- Compile/pin (pip-tools style): `uv pip compile requirements.in -o requirements.txt`
- Sync exactly to pinned requirements: `uv pip sync requirements.txt`
- Show installed distributions: `uv pip freeze`
- Uninstall: `uv pip uninstall <name>`

Running commands:
- If supported by your uv version, prefer `uv run <cmd>` for “run in the project context”.
- Otherwise: create venv + sync deps, then run the command in that environment.

## Repo Files To Look For

- `pyproject.toml`: project metadata and dependency declarations (PEP 621 tools section varies by project)
- `uv.lock`: uv-managed lockfile (do not edit by hand)
- `requirements.in`: unpinned direct dependencies
- `requirements.txt`: pinned dependencies suitable for deterministic installs
- `.python-version`: expected Python version (often used by pyenv/asdf)

## Safety Defaults

- Prefer `sync` over repeated `install` when you need the environment to match a lock/pinned file.
- Keep dependency changes minimal and explain what file is the “source of truth” (and what was regenerated).
