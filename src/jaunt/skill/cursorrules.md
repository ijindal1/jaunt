# Cursor Rules (Jaunt Skill)

Copy/paste into `.cursorrules` (or keep as-is and export via `jaunt skill export`).

## Identity
You are an AI assistant collaborating with a human using Jaunt.

## Core Loop
- Write or refine **spec stubs** (signatures + docstrings + type hints).
- Write or refine **test specs** (pytest, deterministic, no network).
- Ask questions when intent is unclear.
- Run or instruct: `jaunt build` to generate implementation.
- Review generated output with the human, then iterate.

## Hard Rules
- Do not implement any symbol intended to be generated (for example, `@jaunt.magic`).
- Never edit anything under `__generated__/`.
- Do not introduce network calls in tests.
- Prefer dependency injection for I/O and time (pass callables/clients/clock into spec APIs).

## What To Produce
- Spec stubs that are decision-complete: inputs, outputs, errors, edge cases, constraints.
- Tests that encode the contract and cover negatives.
- Minimal config updates (for `jaunt.toml`) when needed.

## Spec Stub Templates
- Pure function: describe transformation + validation + failure mode.
- Dependency function: accept typed callables/protocols for I/O.
- Stateful class: define invariants and method semantics.
- Async function: define retry/backoff, cancellation expectations, error propagation.

