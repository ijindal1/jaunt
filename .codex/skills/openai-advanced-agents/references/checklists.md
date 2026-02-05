# Agent Build Checklists

## Build Checklist (Practical)

1. Define the job:
- Primary tasks (3-10).
- Out-of-scope tasks.
- Success criteria and failure modes.

2. Define the environment:
- Where the agent runs (CLI, server, browser, app).
- What it can access (network, filesystem, APIs).
- Data sensitivity and redaction needs.

3. Define tools:
- List tools and whether they are read-only or mutating.
- For each tool: inputs, outputs, timeouts, retries, error types.
- Validation rules for tool outputs.

4. Define control loop:
- Clarify -> plan -> act -> verify -> respond.
- Max retries and escalation policy.

5. Define state/memory:
- What you persist and why.
- How you avoid storing secrets.

6. Define evals:
- Golden set cases.
- Metrics (success rate, tool errors, latency).
- Regression gating (block deploy if below threshold).

7. Observability:
- Trace IDs.
- Tool-call logs.
- Redaction filters.

## Tool Contract Template

For each tool, document:
- Name:
- Purpose:
- Side effects: none | writes files | calls external APIs | sends messages | other
- Inputs:
- Outputs:
- Error modes:
- Timeouts/retries:
- Permissions/scopes:
- Example calls (1-3):

## Eval Plan Outline

- Task suite: <list>.
- Dataset: <source>.
- Ground truth strategy: <how you judge correctness>.
- Automated checks: schema validation, unit tests, string/regex, LLM-as-judge rubric.
- Human review sampling: <rate>.
- Release gates: <thresholds>.
