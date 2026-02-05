# PROMPT-060: Jaunt CLI (argparse) (L7)

Repo: `/Users/ishitajindal/Documents/jaunt`

## Depends On
- `PROMPT-020` (config)
- `PROMPT-025` (discovery)
- `PROMPT-030` (deps + digests)
- `PROMPT-050` (builder/tester)
- `PROMPT-041` (OpenAI backend) or a FakeBackend wired by flags for tests

## Objective
Replace the placeholder CLI with the MVP commands:
- `jaunt build`
- `jaunt test`

Optionally:
- `jaunt skill export`

CLI tests should be fast: mostly parse tests and light “wiring” tests with mocking.

## Owned Files (avoid editing anything else)
- `src/jaunt/cli.py`
- `src/jaunt/__main__.py`
- `tests/test_cli.py`

Optional cleanup (do not do unless you are comfortable removing scaffolding):
- delete or rewrite `tests/test_basic.py` and remove the `hello()` CLI behavior

## Deliverables

### `src/jaunt/cli.py`
Implement with stdlib `argparse`:

- `parse_args(argv: list[str]) -> argparse.Namespace`
  - Use subcommands `build` and `test`
  - Flags (match TASK-060):
    - common: `--root`, `--config`, `--jobs`, `--force`, `--target` (repeatable), `--no-infer-deps`
    - test: `--no-build`, `--no-run`, `--pytest-args` (repeatable)

- `main(argv: list[str] | None = None) -> int`
  - dispatch to `cmd_build(args)` and `cmd_test(args)`
  - map exceptions to exit codes:
    - 0 success
    - 2 config/discovery error
    - 3 generation error
    - 4 pytest failures

Keep orchestration logic in other modules; CLI should primarily parse args + call into library functions.

### `src/jaunt/__main__.py`
Keep `python -m jaunt` working:
- `raise SystemExit(main())`

## Tests

### `tests/test_cli.py`
Use the TDD plan ideas but align to your actual API:
- parse defaults for `build` and `test`
- parse flags (force/jobs/targets/no-infer-deps/no-build/no-run/pytest-args)
- `--version` exits 0
- light wiring tests:
  - patch `jaunt.cli.cmd_build` / `jaunt.cli.cmd_test` to return specific exit codes; verify `main(...)` returns them

Avoid end-to-end build/test in CLI tests; that belongs in integration tests.

## Quality Gates
```bash
.venv/bin/python -m pytest -q tests/test_cli.py
.venv/bin/python -m ruff check src tests
.venv/bin/python -m ty check
```

## Constraints
- No network calls in tests.
- Keep CLI output minimal (stdout/stderr formatting can be refined later).

