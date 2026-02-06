# Jaunt Docs Revamp — Coding Agent Prompt

## Context

Jaunt is a Python library + CLI for **spec-driven code generation**. You write intent as decorated Python stubs (`@jaunt.magic` for implementations, `@jaunt.test` for tests), and Jaunt uses an LLM to generate real modules under `__generated__/`. The tagline is "jaunt, dont code."

The docs site is built with **Fumadocs (Next.js)** and lives in `docs-site/` within the repo. The content files are `.mdx` under `docs-site/content/docs/`.

## The Problem

The current docs are a reference manual that was copy-pasted from a single `DOCS.md` file and split across pages. They are dry, fragmented, and fail to communicate what makes Jaunt exciting. Specifically:

- No "why" — zero explanation of the philosophy, problem being solved, or differentiation
- No compelling quickstart — the Getting Started page is 10 lines and doesn't deliver any "aha" moment
- No mental model — users can't visualize the generation flow or understand what the LLM sees
- Concepts pages are just API reference dressed up as concepts
- Guides overlap heavily (hackathon-demo, examples, toy-example are ~the same thing)
- No consumer install instructions (assumes you're working from the Jaunt repo)
- The "wow gap" story (tiny spec → lots of real code) isn't front-and-center
- Limitations are buried and under-explained

## Voice & Tone

Match the "jaunt, dont code." energy:
- **Confident and opinionated** — Jaunt has a clear point of view on how AI code generation should work
- **Concise** — developers hate fluff; say it once, say it well
- **Show don't tell** — lead with code examples, not paragraphs of explanation
- **Playful but not gimmicky** — a little personality goes a long way; don't try too hard
- **Honest about limitations** — MVP energy; be upfront about what's rough

Think: Stripe docs clarity meets indie hacker energy. Not corporate, not academic.

## New Information Architecture

Replace the current structure entirely. Here's the new sitemap with content direction for each page.

### `meta.json` (root)

```json
{
  "title": "Jaunt",
  "pages": ["index", "quickstart", "how-it-works", "writing-specs", "guides", "reference", "development"]
}
```

---

### 1. `index.mdx` — Landing / "Why Jaunt"

**Purpose:** Hook developers in 30 seconds. Communicate the value prop, show the wow gap, and get them to click "Quickstart."

**Structure:**
- Hero heading: "jaunt, dont code." with a one-liner subtitle
- **The Pitch (3-4 sentences max):** You write specs (Python stubs with docstrings + types). Jaunt generates real implementations + tests using an LLM. You review and iterate. The spec is the contract — everything flows from it.
- **The Wow Gap — side-by-side:** Show a ~15-line `@jaunt.magic` spec on the left, and excerpts of the ~80-line generated implementation on the right (use the JWT `create_token` example — it's the best one). The visual contrast IS the pitch. Use Fumadocs tabs or a two-column layout.
- **Why not just prompt an LLM directly?** (3-4 bullet points, not a wall of text)
  - Specs are **versionable** — they live in your repo as real Python, not ephemeral chat
  - **Incremental rebuilds** — Jaunt tracks digest hashes; only regenerates when specs change
  - **Dependency ordering** — specs can depend on other specs; Jaunt builds them in the right order
  - **Runtime forwarding** — `@jaunt.magic` functions work as real imports; call them like normal Python
- Cards linking to: Quickstart, How It Works, Writing Specs

**What to cut from the current `index.mdx`:** Everything. The current version is just the DOCS.md intro paragraph. Start fresh.

---

### 2. `quickstart.mdx` — Zero to Wow in 5 Minutes

**Purpose:** Get someone from `pip install` to seeing generated code as fast as possible. This is the #1 most important page.

**Structure:**
1. **Install** — `uv add jaunt` or `pip install jaunt` (check if it's on PyPI; if not, show the git install). Also: `export OPENAI_API_KEY=...`
2. **Create `jaunt.toml`** — show the minimal 6-line config
3. **Write your first spec** — use the `normalize_email` example (simple, universally understood). Show the full file with imports and decorator. Briefly annotate: "The docstring is your contract. The type hints matter. The body is a placeholder."
4. **Generate** — `jaunt build`. Show what happens: "Jaunt reads your spec, sends it to OpenAI, and writes a real module to `src/my_app/__generated__/specs.py`."
5. **Use it** — Show calling the generated function:
   ```python
   from my_app.specs import normalize_email
   print(normalize_email("  A@B.COM  "))  # → "a@b.com"
   ```
   Emphasize: "You import your spec module, not the generated one. The `@jaunt.magic` decorator handles forwarding."
6. **Add a test spec** — Show writing a `@jaunt.test` stub, then `jaunt test`. "Jaunt generates real pytest tests and runs them."
7. **What's next** — links to How It Works and Writing Specs

**Critical:** This must be a complete, copy-paste-able tutorial. Someone should be able to follow this end-to-end without reading any other page. Include the full project layout tree at the start.

---

### 3. `how-it-works.mdx` — Mental Model

**Purpose:** Give developers a clear picture of what happens under the hood, without being a code walkthrough.

**Structure:**
1. **The Flow (use a Mermaid diagram or ASCII art):**
   ```
   You write specs → Jaunt discovers them → builds dependency graph →
   sends each spec to LLM (with deps context) → validates output →
   writes to __generated__/ → runtime decorator forwards calls
   ```
2. **What the LLM sees** — Describe the prompt structure: system prompt (from `src/jaunt/prompts/`) + your spec's source segment + docstring + type hints + any dependency context + any auto-generated PyPI skills. The LLM's job is to implement the contract.
3. **Incremental rebuilds** — Explain the digest system: Jaunt hashes each spec's source. Generated files have a header with the digest. On re-run, only stale specs get regenerated.
4. **Runtime forwarding** — When you call a `@jaunt.magic` function, the decorator imports the corresponding `__generated__` module and delegates. If the generated module doesn't exist yet, you get `JauntNotBuiltError`.
5. **Dependency ordering** — Jaunt builds a DAG from explicit `deps=` and inferred edges. Deps get generated first. A change to a dependency makes its dependents stale too.
6. **PyPI skills injection (optional, brief)** — During build, Jaunt scans your imports, fetches PyPI READMEs, generates "skill" docs, and injects them into the LLM prompt so it knows how to use your libraries correctly.

**Tone:** Explanatory but not exhaustive. Point to reference pages for specifics. This page is about building intuition.

---

### 4. `writing-specs/` — The Core Skill

This section replaces the old "concepts" section and makes it actually useful.

#### `meta.json`
```json
{
  "title": "Writing Specs",
  "pages": ["magic", "test-specs", "dependencies", "tips"]
}
```

#### 4a. `magic.mdx` — `@jaunt.magic` Specs

**Purpose:** Everything you need to write good implementation specs.

**Structure:**
- **The basics** — recap what `@jaunt.magic` does (decorate a function or class stub; Jaunt generates the real implementation)
- **Anatomy of a good spec:**
  - Signature: type hints are part of the contract
  - Docstring: this IS the specification — be precise about behavior, edge cases, errors
  - Body: doesn't matter (convention: `raise RuntimeError("spec stub")`)
- **Full annotated example** — use the `is_corporate_email` example with `deps=normalize_email`. Annotate each piece with comments explaining why it's there.
- **Decorator options:** `deps=`, `prompt=`, `infer_deps=` — each with a one-line explanation and example
- **Classes too** — brief example of a `@jaunt.magic` class

**What to add that's currently missing:**
- "What makes a good docstring?" — Be specific about expected behavior. Name edge cases. Give examples. Think of it like writing a really good ticket, not code comments.
- "What if the LLM generates garbage?" — Edit your spec to be more precise, add `prompt=` for extra context, and re-run. Jaunt re-generates stale specs.

#### 4b. `test-specs.mdx` — `@jaunt.test` Specs

**Purpose:** How to write test intent stubs.

**Structure:**
- **What these are (and aren't)** — They are NOT tests. They are descriptions of what tests should do. The LLM generates the real test code.
- **Rules:** top-level functions, `test_*` naming, `__test__ = False` on stubs
- **Annotated example** — the `test_normalize_email__lowercases_and_strips` example, annotated
- **Tips:**
  - Be explicit about assertions: "assert X == Y" in the docstring, not "check that it works"
  - Include edge cases: invalid inputs, boundary values
  - Reference the spec function by import so the LLM knows what to test

#### 4c. `dependencies.mdx` — Dependencies

**Keep the current content** but add:
- **When to use explicit `deps=` vs inference** — Inference is best-effort and may miss things. Use explicit deps when: (a) the dependency is in a different module, (b) you want guaranteed ordering, (c) inference is getting it wrong.
- **What happens during generation** — Dependencies are generated first. Their generated source is (currently) NOT passed as context to dependents (limitation), but ordering and digest propagation still work.

#### 4d. `tips.mdx` — Spec Writing Tips (NEW)

**Purpose:** Practical advice that doesn't fit in the reference-style pages.

**Content:**
- **Writing effective docstrings** — examples of vague vs. precise specs (show both and explain why the precise one generates better code)
- **Using `prompt=` for extra context** — when the docstring isn't enough (e.g., "Use the `cryptography` library, not `hashlib`")
- **Iterating on specs** — The workflow is: write spec → generate → review output → refine spec → regenerate. This loop IS the development process.
- **When NOT to use Jaunt** — Complex stateful logic, performance-critical hot paths, code that needs precise library version handling. Jaunt is best for: glue code, parsers, validators, formatters, boring-but-correct utilities.

---

### 5. `guides/` — Practical Walkthroughs

Consolidate the current 4 overlapping guides into 2 focused ones.

#### `meta.json`
```json
{
  "title": "Guides",
  "pages": ["jwt-walkthrough", "adding-to-your-project", "pypi-skills"]
}
```

#### 5a. `jwt-walkthrough.mdx` — The Hero Demo (MERGE: hackathon-demo + examples)

**Purpose:** A fully narrated walkthrough of the JWT auth demo — the best "wow gap" story.

**Structure:**
1. **What we're building** — a JWT token creator/verifier from a ~30-line spec
2. **The spec** — show the full `specs.py` (Claims model, create_token, verify_token)
3. **Run the build** — `jaunt build --root jaunt-examples/jwt_auth`
4. **Look at the output** — show excerpts of the generated implementation (base64url encoding, HMAC signing, expiry checks). Highlight: "You wrote 30 lines. Jaunt generated 100+ lines of correct, edge-case-handling code."
5. **Generate and run tests** — `jaunt test --root jaunt-examples/jwt_auth`. Show test excerpts.
6. **The skills bonus** — Jaunt auto-generated a pydantic skill because the spec imports it.

**Absorbs content from:** hackathon-demo.mdx, examples.mdx, toy-example.mdx. Kill those pages.

#### 5b. `adding-to-your-project.mdx` — Adding Jaunt to an Existing Project (NEW)

**Purpose:** Consumer-perspective guide (not "using this repo").

**Structure:**
1. Install Jaunt
2. Create `jaunt.toml` in your project root
3. Identify a good candidate for your first spec (a utility function, a parser, a validator)
4. Write the spec stub in your existing source tree
5. Run `jaunt build`
6. Import and use the generated code
7. Commit the spec AND the generated code (or `.gitignore` the generated dir — discuss tradeoffs)

#### 5c. `pypi-skills.mdx` — Auto-Generated PyPI Skills

**Keep the current content mostly as-is.** It's the one guide page that's already decent. Minor cleanup:
- Add a brief intro sentence explaining why this matters (better LLM output for code that uses external libraries)
- Clean up the troubleshooting section

---

### 6. `reference/` — Dry Reference (This Is Where Dry Is Fine)

#### `meta.json`
```json
{
  "title": "Reference",
  "pages": ["cli", "config", "output", "openai-backend", "limitations"]
}
```

**Keep all 5 current reference pages.** They're already appropriately reference-style. Minor edits:

- **`cli.mdx`** — Add a note at the top: "For a guided introduction, see the Quickstart." Remove the PyPI skills section (it now lives in guides).
- **`config.mdx`** — Add brief inline comments explaining each config key (some are non-obvious, like `infer_deps`).
- **`limitations.mdx`** — Expand each bullet into 2-3 sentences. Currently they're too terse to be useful. For example, the hardcoded `__generated__` limitation should explain: "This means if you set `paths.generated_dir` to a custom name, `jaunt build` will write files there, but calling your `@jaunt.magic` functions at runtime will fail because the decorator looks for `__generated__/`. Workaround: import the generated module directly."
- **`output.mdx`** and **`openai-backend.mdx`** — fine as-is with light copy editing.

---

### 7. `development/` — Contributing

#### `meta.json`
```json
{
  "title": "Development",
  "pages": ["contributing", "architecture-notes"]
}
```

**Keep both pages as-is.** They're internal-facing and fine for that purpose.

---

## Implementation Checklist

Work through these in order:

### Phase 1: Structure

1. [ ] Update `docs-site/content/docs/meta.json` with new top-level page order
2. [ ] Create new directories: `writing-specs/` (replacing `concepts/`)
3. [ ] Create new `meta.json` files for each section
4. [ ] Delete old files that are being replaced: `concepts/magic.mdx`, `concepts/test-specs.mdx`, `concepts/dependencies.mdx`, `concepts/meta.json`, `guides/hackathon-demo.mdx`, `guides/examples.mdx`, `guides/toy-example.mdx`, `guides/meta.json`

### Phase 2: New Pages (write these first — they're net-new content)

5. [ ] Write `index.mdx` — the landing/why page with wow-gap side-by-side
6. [ ] Write `quickstart.mdx` — complete end-to-end tutorial
7. [ ] Write `how-it-works.mdx` — mental model with flow diagram
8. [ ] Write `writing-specs/tips.mdx` — practical spec-writing advice
9. [ ] Write `guides/jwt-walkthrough.mdx` — consolidated hero demo walkthrough
10. [ ] Write `guides/adding-to-your-project.mdx` — consumer setup guide

### Phase 3: Revised Pages (rewrite existing content with new framing)

11. [ ] Rewrite `writing-specs/magic.mdx` — add "what makes a good spec" content
12. [ ] Rewrite `writing-specs/test-specs.mdx` — add practical tips
13. [ ] Revise `writing-specs/dependencies.mdx` — add "when to use" guidance
14. [ ] Revise `guides/pypi-skills.mdx` — add intro context, light cleanup
15. [ ] Revise `reference/cli.mdx` — add quickstart cross-reference, remove skills section
16. [ ] Revise `reference/config.mdx` — add inline comments
17. [ ] Expand `reference/limitations.mdx` — flesh out each limitation

### Phase 4: Cross-References & Polish

18. [ ] Add "Next: ..." links at the bottom of each page pointing to the logical next read
19. [ ] Ensure all code examples are copy-paste-able (full imports, no ellipsis in critical places)
20. [ ] Verify all internal links between pages are correct
21. [ ] Remove `DOCS.md` from the repo root (or add a note that the docs site is canonical)

---

## Content to Reuse

All of the raw content you need already exists. Here's where to find it:

| New Page | Source Content |
|----------|---------------|
| `index.mdx` (wow gap) | JWT spec: `jaunt-examples/jwt_auth/src/jwt_demo/specs.py`. Generated output excerpts: current `guides/examples.mdx` |
| `quickstart.mdx` | `DOCS.md` sections: "Quickstart", "Minimal Consumer Project Layout", "@jaunt.magic Specs", "@jaunt.test Specs", "CLI" |
| `how-it-works.mdx` | `DOCS.md` sections: "Dependencies", "Backend: OpenAI", "Where Output Goes". Also `TASK-040-GENERATION-BACKENDS.md` for backend details |
| `writing-specs/magic.mdx` | Current `concepts/magic.mdx` + `DOCS.md` "@jaunt.magic Specs" section |
| `writing-specs/test-specs.mdx` | Current `concepts/test-specs.mdx` + `DOCS.md` "@jaunt.test Specs" section |
| `writing-specs/dependencies.mdx` | Current `concepts/dependencies.mdx` + `DOCS.md` "Dependencies" section |
| `guides/jwt-walkthrough.mdx` | Current `guides/hackathon-demo.mdx` + `guides/examples.mdx` (JWT section) + `guides/toy-example.mdx` |
| `guides/adding-to-your-project.mdx` | New content, but reference `DOCS.md` "Minimal Consumer Project Layout" and "jaunt.toml" sections |

---

## Fumadocs-Specific Notes

- Use Fumadocs `<Cards>` and `<Card>` components for navigation blocks
- Use Fumadocs `<Tabs>` and `<Tab>` components for the wow-gap side-by-side on the landing page
- Use Fumadocs `<Callout>` component for warnings/tips (e.g., "This will call the OpenAI API and spend tokens")
- Use `<Steps>` component if available for the quickstart numbered flow
- All files are `.mdx` with YAML frontmatter (`title`, `description`)
- Mermaid diagrams work if the Fumadocs config supports them; otherwise use a code block with ASCII art

---

## Final Notes

- **Don't pad pages.** If a page only needs 40 lines, that's fine. Short and useful beats long and comprehensive.
- **Every page should answer "why am I reading this?"** in the first 2 sentences.
- **Code examples are king.** When in doubt, show code. Annotate with comments, not prose.
- **The quickstart is the most important page.** Spend the most time on it. It should be so good that someone can go from zero to generated code without reading anything else.
