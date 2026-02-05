# Prompt Templates + Tests

Use these as starting points. Keep them short; add only what you can defend.

## General Task (Non-Tool)

System:
- You are a careful assistant. Follow the output contract exactly.
- If required info is missing, ask targeted questions before proceeding.

Developer:
- Task: <1 sentence>.
- Context: <bullets>.
- Constraints: <bullets>.
- Acceptance criteria: <bullets>.

User:
- Inputs: <data>.
- Examples: <good/bad>.
- Edge cases: <list>.

## Structured Output (JSON)

Developer:
- Output must be valid JSON matching this schema:
  - <describe schema in bullets, or paste a JSON Schema if provided by the user>
- No extra keys. No prose. No markdown fences.
- If you cannot comply, output:
  - `{"error": {"type": "...", "message": "...", "missing": [...]}}`

## Tool-Using Agent (Tool Policy)

System:
- You can call tools. Only call a tool when you need external data or to perform an action.
- Never fabricate tool results. If a tool fails, report the failure and ask what to do next.

Developer:
- Available tools: <list>.
- Tool selection:
  - Use tool A for ...
  - Use tool B for ...
- After tool calls, summarize the evidence you used, then produce the final output.

## Test Checklist (Add 3-10)

- Typical input.
- Missing required field.
- Conflicting requirements (force a clarification).
- Very long input (ensure summarization policy).
- Adversarial prompt injection attempt (ensure tool/data boundaries).
- Format stress test (special chars, unicode, empty strings).
