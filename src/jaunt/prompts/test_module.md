Output Python code only (no markdown, no fences).

Write pytest tests for generated module `{{generated_module}}` based on specs from `{{spec_module}}`.

Required names to import/test: {{expected_names}}

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
- Do not edit user files; only output test module source code.

