# TASK-070: Layer 3 Skill Docs (AI Assistant UX)

## Objective
Create the “Jaunt skill” documentation that teaches user-facing AI assistants (Cursor/Claude/Copilot) how to collaborate with humans in the Jaunt workflow.

This is primarily a writing task, but it may require small packaging/CLI changes to ship/export the docs.

## Core Philosophy (must be explicit)
The AI assistant writes **intent** (specs). Jaunt generates **implementation**. The human reviews both.
The AI assistant should not short-circuit the loop by writing implementations directly unless the user insists and understands the tradeoff.

## Deliverables
### Docs (shipped with the package)
Add under `src/jaunt/skill/`:
- `SKILL.md` (canonical)
- `cursorrules.md` (same content adapted to `.cursorrules` style)
- `examples/`
  - `basic_function_spec.py`
  - `class_spec.py`
  - `test_spec.py`
  - `jaunt.toml`

### Packaging
Ensure these files are included in the wheel built by hatchling.
- If hatchling config is needed, add the minimal `tool.hatch.build` include patterns.

### CLI (optional but recommended)
Implement/extend `jaunt skill export`:
- Writes the packaged skill docs into a user project directory.
- Default destination: current working directory.
- Writes into a subdir like `jaunt-skill/` to avoid cluttering root.

## SKILL.md Structure (decision-complete)
1. What is Jaunt (1 paragraph, AI-parseable)
2. Your Role as an AI Assistant
   - You help write/refine spec stubs and test specs.
   - You do not write implementations for `@jaunt.magic` symbols.
3. Workflow you should guide
   - Write specs -> `jaunt build` -> review generated -> iterate
4. Writing good spec stubs (largest section)
   - principles, patterns, anti-patterns
   - include templates for: pure function, deps, stateful class, async function
5. Writing good test specs
   - principles, patterns, anti-patterns
6. Configuration reference (jaunt.toml)
7. Critical rules
   - never edit `__generated__/`
   - always regenerate via CLI
   - always review generated output

## Tests
Not required beyond basic packaging sanity, but optionally add one test ensuring packaged resources exist (importlib.resources).

## Copy/Paste Prompt (for a separate agent)
You are implementing TASK-070 in the repo at `/Users/ishitajindal/Documents/jaunt`.

Do:
- Write the docs under `src/jaunt/skill/` as specified.
- Ensure packaging includes these resources.
- Optionally implement `jaunt skill export` if not already implemented in TASK-060.

Constraints:
- Keep docs concise but highly actionable.
- The docs are for AI assistants first; humans should still be able to read them.

Quality gates:
- `uv run ruff check .`
- `uv run ty check`
- `uv run pytest`

