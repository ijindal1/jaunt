Output Python code only (no markdown, no fences).

You are generating the pytest test module `{{generated_module}}` from test specs in `{{spec_module}}`.

The generated module MUST define these top-level pytest test functions (do not import them): {{expected_names}}

Specs:
{{specs_block}}

Dependency APIs (callable signatures/docstrings):
{{deps_api_block}}

Previously generated dependency modules (reference only):
{{deps_generated_block}}

Extra error context (fix these issues):
{{error_context_block}}

Rules:
- Generate tests only (no production implementation).
- Do not import from `{{generated_module}}` (that would be a circular import).
- Do not edit user files; only output test module source code.
- Do not guess or search for application modules like `app`, `main`, `token`, etc.
- Import the production APIs under test from the modules listed in Dependency APIs above.
  - Each Dependency API entry key is like `<module>:<qualname>`; import from `<module>`.
- Do not import production APIs from the test spec module (`{{spec_module}}`); it contains only `@jaunt.test` stubs.
