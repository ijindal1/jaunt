# TASK-060: Jaunt CLI (Layer 2 UX)

## Objective
Implement the `jaunt` command-line interface that wires together:
- config loading
- discovery/import of spec modules
- dependency graph + digests
- builder/tester orchestration

This task should not implement the OpenAI backend internals or the digest algorithms; it should compose them.

## Deliverables
### Code
- Update/replace `src/jaunt/cli.py` to support:

#### `jaunt build`
Flags:
- `--root PATH` (default: search upward from cwd for `jaunt.toml`)
- `--config PATH` (default: `<root>/jaunt.toml`)
- `--jobs N` (override config)
- `--force`
- `--target MODULE[:QUALNAME]` (repeatable)
- `--no-infer-deps`

Behavior:
- load config
- discover + import source spec modules (exclude `__generated__`)
- build graphs/digests, select stale modules
- call builder scheduler
- print summary + exit with codes:
  - 0 success
  - 2 config/discovery error
  - 3 generation error

#### `jaunt test`
Flags:
- all `build` flags
- `--no-build`
- `--no-run`
- `--pytest-args ARG` (repeatable; appended)

Behavior:
- optionally run `build`
- discover + import test spec modules
- generate tests via tester
- optionally run pytest via tester
- exit codes:
  - 0 success
  - 2 config/discovery error
  - 3 generation error
  - 4 pytest failures

#### (Optional but recommended) `jaunt skill export`
Flags:
- `--dest PATH` (default: cwd)
- `--force`

Behavior:
- write packaged skill docs + examples into `<dest>/jaunt-skill/` (or similar)
- print where they were written

### Tests
Under `tests/`:
- CLI parsing tests for `build` and `test` options
- end-to-end CLI tests using tmp projects and FakeBackend (can be minimal if TASK-050 already covers integration)

## Copy/Paste Prompt (for a separate coding agent)
You are implementing TASK-060 in the repo at `/Users/ishitajindal/Documents/jaunt`.

Do:
- Implement CLI in `src/jaunt/cli.py` with subcommands described above.
- Add CLI-focused tests.

Constraints:
- Use stdlib `argparse` in MVP (avoid adding click/typer until needed).

Quality gates:
- `uv run ruff check .`
- `uv run ty check`
- `uv run pytest`

