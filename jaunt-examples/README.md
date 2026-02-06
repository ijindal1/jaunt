# Jaunt Examples (Hackathon Demos)

Jaunt is built for the "wow gap": the spec is 10 lines, but the implementation is 80+ lines of boring edge cases, tests, and glue. These demos are small consumer projects that run Jaunt as an external tool, like you would in a real repo.

## Examples

- JWT auth (`jwt`): base64/HMAC signing + expiry checks; `pydantic` usage triggers skills.
- Markdown renderer (`markdown`): a small state machine for parsing + escaping.
- Rate limiter (`limiter`): sliding window with pruning and clock injection.
- CSV parser (`csv`): coercion plus strict vs lenient modes.

## Run

From the repo root:

```bash
.venv/bin/python jaunt-examples/run_example.py jwt test
.venv/bin/python jaunt-examples/run_example.py markdown build
.venv/bin/python jaunt-examples/run_example.py limiter test --no-run
.venv/bin/python jaunt-examples/run_example.py csv build --force
```

Notes:

- Running these commands calls OpenAI and will spend tokens (set `OPENAI_API_KEY`).
- Generated code is written under `<example_root>/**/__generated__/` and is gitignored.
- Generated skills land under `<example_root>/.agents/skills/**/SKILL.md` and are gitignored.
