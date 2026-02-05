---
name: fumadocs-docs
description: "Use when setting up, migrating to, or maintaining a Fumadocs (Next.js) documentation site for this repo, including: creating/editing MDX pages, organizing doc routes/navigation, configuring search/theming, and ensuring docs content matches the Python codebase and existing markdown docs."
---

# Fumadocs Docs

## Overview

Create a Fumadocs-powered documentation website for this repository and keep it accurate as the code evolves. Use it for both initial setup (adding a docs app) and ongoing authoring (new pages, navigation changes, refinements).

## Repo Context (Jaunt)

- Treat these files as the current canonical written sources for Jaunt behavior and CLI/config usage:
  - `README.md`
  - `DOCS.md`
  - `TASK-*.md` and `jaunt_tdd_plan.md` (design/architecture notes; link to them rather than duplicating verbatim when possible)
- The code lives under `src/jaunt/`; doc pages should reference real module names, CLI flags, and config keys.

## References

- Start with `references/fumadocs-llms.txt` to find the most relevant Fumadocs docs pages for installation, content authoring, routing, and customization. The links in that file are relative to `https://www.fumadocs.dev`.
- Use `references/jaunt-doc-sources.md` as a quick index of existing repo documentation to convert or link into the docs site.

## Workflow: Create A Fumadocs Site In This Repo

1. Choose a docs app directory (recommended: `docs-site/` at the repo root) to avoid colliding with Python package paths.
2. Initialize the Next.js app in that directory.
3. Install and configure Fumadocs by following the official Fumadocs docs (use the `references/fumadocs-llms.txt` index; do not guess package names or config APIs).
4. Create a minimal set of pages that mirror the repo’s current docs:
   - Home / overview (based on `README.md`)
   - Getting started / quickstart (based on `DOCS.md`)
   - CLI reference (from `DOCS.md` and `src/jaunt/cli.py` or equivalent entrypoint)
   - Configuration reference (`jaunt.toml` keys from `DOCS.md` and the config loader)
5. Add navigation and sidebars matching the page structure.
6. Validate by running the docs app dev server and a production build (commands depend on the chosen package manager; keep them consistent within the docs app).

## Workflow: Add Or Update Documentation Pages

1. Identify the source of truth in the code and existing docs:
   - Prefer documenting behavior already validated by tests (`tests/`) and described in `DOCS.md`.
2. Create or edit the MDX page in the Fumadocs content location configured by the site.
3. Keep docs precise and testable:
   - Include concrete CLI commands and expected outputs where appropriate.
   - Prefer small code snippets that compile/run over long pseudo-code.
4. Update navigation/metadata so the page is discoverable.
5. Check internal links and headings render correctly (MDX).
6. Ensure the page matches the current code (names, flags, defaults).

## Conventions For MDX Content

- Use one top-level `#` title per page.
- Use fenced code blocks with language tags (e.g. `bash`, `toml`, `python`) and keep examples runnable.
- Prefer relative links to other docs pages; link to repo files when referencing implementation details.
- Avoid duplicating long sections from `TASK-*.md`; summarize and link instead.

## Common Tasks

- **Create a “Getting Started” section**: convert the “Quickstart” and minimal `jaunt.toml` sections from `DOCS.md` into MDX pages.
- **Create a CLI reference**: document flags/subcommands exactly as implemented; keep examples aligned with tests and current behavior.
- **Document generation workflow**: explain `@jaunt.magic` / `@jaunt.test` stubs, where `__generated__/` output lands, and how to iterate safely.

## Quality Bar

- If you are unsure about Fumadocs APIs or configuration, consult the official docs first (use `references/fumadocs-llms.txt` to find the relevant page).
- Keep docs changes small and reviewable: add a page, wire nav, verify build, then iterate.
