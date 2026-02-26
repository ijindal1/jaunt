# jaunt

**jaunt, don't code.** Spec-driven code generation for Python.

Vibe coding is fast but fragile — you get working code with no structure, no tests, and no way to maintain it. Writing every line by hand gives you control but kills your speed. Jaunt is the middle path: you write **specs** (type hints + docstrings + dependency declarations), and an LLM generates the implementation.

You keep the architecture. The machine writes the code.

## How It Works

1. **Write specs** — Python stubs decorated with `@jaunt.magic(...)`. Types, docstrings, and contracts define *what* you want. The body is ignored.
2. **`jaunt build`** — Jaunt resolves dependencies, builds a DAG, and generates real modules under `__generated__/` using an LLM backend (OpenAI). Only stale modules are regenerated.
3. **`jaunt test`** — Optionally write test stubs with `@jaunt.test(...)`. Jaunt generates real pytest tests and runs them.

## Example: JWT Auth in ~60 Lines of Spec

```python
"""JWT Authentication — Jaunt Example"""

from __future__ import annotations
from datetime import timedelta

import jaunt
from pydantic import BaseModel


class Claims(BaseModel):
    """Decoded token payload."""
    sub: str   # subject (user id)
    iat: float # issued-at (unix timestamp)
    exp: float # expiry (unix timestamp)


@jaunt.magic()
def create_token(
    user_id: str,
    secret: str,
    *,
    ttl: timedelta = timedelta(hours=1),
) -> str:
    """
    Create an HS256-signed JWT.

    Structure: base64url(header) . base64url(payload) . base64url(signature)
    Header:  {"alg": "HS256", "typ": "JWT"}
    Payload: {"sub": user_id, "iat": <now>, "exp": <now + ttl>}

    - Use HMAC-SHA256 with `secret` as the key.
    - base64url encoding must omit padding ("=" characters).
    - Raise ValueError if user_id is empty.
    """
    ...


@jaunt.magic(deps=[create_token, Claims])
def verify_token(token: str, secret: str) -> Claims:
    """
    Verify an HS256-signed JWT and return its claims.

    1. Split token on "." — must have exactly 3 parts.
    2. Recompute HMAC-SHA256 over header.payload; compare to signature.
    3. Decode payload JSON into Claims.
    4. Check exp > current time.

    Errors:
    - ValueError("malformed") if structure is wrong.
    - ValueError("invalid signature") if HMAC doesn't match.
    - ValueError("expired") if token has expired.
    """
    ...


@jaunt.magic(deps=[create_token, verify_token])
def rotate_token(token: str, secret: str, *, ttl: timedelta = timedelta(hours=1)) -> str:
    """
    Verify an existing token and issue a fresh one for the same subject.

    - Verify the old token (propagate any errors).
    - Create a new token with the same user_id and a fresh ttl.
    """
    ...
```

From this spec, Jaunt generates a complete HS256 JWT implementation — base64url encoding, HMAC signing, expiry validation, token rotation — plus matching pytest tests. Your IDE sees the types. Your code reviews read the specs. The generated code lives in `__generated__/` and never needs to be touched.

## Quickstart

Prerequisites: [`uv`](https://docs.astral.sh/uv/) and an OpenAI API key.

```bash
uv sync
export OPENAI_API_KEY=...

# Generate implementations from specs
uv run jaunt build --root jaunt-examples/jwt_auth

# Generate tests and run them
PYTHONPATH=jaunt-examples/jwt_auth/src uv run jaunt test --root jaunt-examples/jwt_auth
```

See `jaunt-examples/` for more demo projects, `toy-example/` for a minimal setup, and `docs-site/` for full documentation.

## Features

- **Spec-driven** — Type hints and docstrings are the contract. Your specs are real Python that IDEs, type checkers, and humans can all read.
- **Dependency graph** — Declare deps explicitly (`deps=[fn_a, ClassB]`) or let Jaunt infer them. Modules build in topological order with configurable concurrency.
- **Incremental rebuilds** — Content-hashed digests track spec changes. Only stale modules (and their transitive dependents) are regenerated.
- **Auto-skills** — Jaunt scans your imports, resolves them to PyPI packages, fetches their docs, and injects that context into the LLM prompt so it knows how to use your dependencies.
- **Test generation** — `@jaunt.test` stubs describe test intent. Jaunt generates real pytest functions and runs them.
- **Validation + retry** — Generated code is checked for expected top-level symbols. On failure, errors are fed back to the LLM for a second attempt.

## Project Layout

```
src/jaunt/          # Library + CLI
src/jaunt/prompts/  # Default prompt templates
src/jaunt/generate/ # LLM backends (OpenAI)
tests/              # Test suite
jaunt-examples/     # Consumer-style demo projects (JWT auth, CSV parser, etc.)
docs-site/          # Fumadocs documentation site
DOCS.md             # Full technical reference
```

## Dev

```bash
uv run ruff check .
uv run ty check
uv run pytest
```
