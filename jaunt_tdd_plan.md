# Jaunt MVP — TDD Test Plan

> Write each test file BEFORE implementing the corresponding task.
> Tests are ordered by dependency level — you can write and run all tests
> for a level as soon as the previous level's implementation is done.
> Tests are intentionally simple and fast. No LLM calls, no I/O where avoidable.

---

## Phase 1: Foundations (L0)

### T1 — `tests/test_errors.py`

```python
"""Tests for jaunt/errors.py — exception hierarchy."""

from jaunt.errors import (
    JauntError,
    JauntConfigError,
    JauntDiscoveryError,
    JauntNotBuiltError,
    JauntGenerationError,
    JauntDependencyCycleError,
)


def test_base_error_is_exception():
    assert issubclass(JauntError, Exception)


def test_config_error_is_jaunt_error():
    assert issubclass(JauntConfigError, JauntError)


def test_discovery_error_is_jaunt_error():
    assert issubclass(JauntDiscoveryError, JauntError)


def test_not_built_error_is_jaunt_error():
    assert issubclass(JauntNotBuiltError, JauntError)


def test_generation_error_is_jaunt_error():
    assert issubclass(JauntGenerationError, JauntError)


def test_cycle_error_is_jaunt_error():
    assert issubclass(JauntDependencyCycleError, JauntError)


def test_all_catchable_as_jaunt_error():
    """Catch any jaunt exception with `except JauntError`."""
    for exc_class in [
        JauntConfigError,
        JauntDiscoveryError,
        JauntNotBuiltError,
        JauntGenerationError,
        JauntDependencyCycleError,
    ]:
        try:
            raise exc_class("test")
        except JauntError:
            pass  # should be caught


def test_error_message_preserved():
    err = JauntNotBuiltError("Run `jaunt build` first")
    assert "jaunt build" in str(err)
```

---

### T2 — `tests/test_spec_ref.py`

```python
"""Tests for jaunt/spec_ref.py — canonical spec identity."""

from jaunt.spec_ref import normalize_spec_ref, spec_ref_from_object


def test_normalize_colon_format():
    assert normalize_spec_ref("my_project.foo:bar") == "my_project.foo:bar"


def test_normalize_dot_shorthand():
    """my_project.foo.bar → my_project.foo:bar"""
    assert normalize_spec_ref("my_project.foo.bar") == "my_project.foo:bar"


def test_normalize_single_module_dot():
    """foo.bar → foo:bar"""
    assert normalize_spec_ref("foo.bar") == "foo:bar"


def test_normalize_already_canonical_is_idempotent():
    ref = "pkg.mod:MyClass"
    assert normalize_spec_ref(ref) == ref


def test_normalize_nested_qualname():
    """pkg.mod:Outer.Inner stays as-is (qualname can have dots)."""
    assert normalize_spec_ref("pkg.mod:Outer.Inner") == "pkg.mod:Outer.Inner"


def test_spec_ref_from_object_function():
    def dummy():
        pass

    dummy.__module__ = "my_project.utils"
    dummy.__qualname__ = "dummy"
    assert spec_ref_from_object(dummy) == "my_project.utils:dummy"


def test_spec_ref_from_object_class():
    class Greeter:
        pass

    Greeter.__module__ = "my_project.greet"
    Greeter.__qualname__ = "Greeter"
    assert spec_ref_from_object(Greeter) == "my_project.greet:Greeter"
```

---

### T3 — `tests/test_pyproject.py`

```python
"""Tests for pyproject.toml — verify project metadata and dependencies."""

import tomllib
from pathlib import Path


def test_pyproject_parseable():
    path = Path(__file__).parent.parent / "pyproject.toml"
    with open(path, "rb") as f:
        data = tomllib.load(f)
    assert "project" in data


def test_has_openai_dependency():
    path = Path(__file__).parent.parent / "pyproject.toml"
    with open(path, "rb") as f:
        data = tomllib.load(f)
    deps = data["project"].get("dependencies", [])
    assert any("openai" in d for d in deps)


def test_has_cli_entrypoint():
    path = Path(__file__).parent.parent / "pyproject.toml"
    with open(path, "rb") as f:
        data = tomllib.load(f)
    scripts = data["project"].get("scripts", {})
    assert "jaunt" in scripts
```

---

### T4 — `tests/test_header.py`

```python
"""Tests for jaunt/header.py — generated file header format + parsing."""

from jaunt.header import format_header, parse_header, extract_module_digest


def test_format_header_contains_warning():
    h = format_header(
        tool_version="0.1.0",
        kind="build",
        source_module="my_project.foo",
        module_digest="sha256:abc123",
        spec_refs=["my_project.foo:bar"],
    )
    assert "DO NOT EDIT" in h


def test_format_header_contains_all_fields():
    h = format_header(
        tool_version="0.1.0",
        kind="build",
        source_module="my_project.foo",
        module_digest="sha256:abc123",
        spec_refs=["my_project.foo:bar", "my_project.foo:baz"],
    )
    assert "jaunt:kind=build" in h
    assert "jaunt:source_module=my_project.foo" in h
    assert "jaunt:module_digest=sha256:abc123" in h


def test_parse_header_roundtrip():
    original = dict(
        tool_version="0.1.0",
        kind="test",
        source_module="tests.specs",
        module_digest="sha256:deadbeef",
        spec_refs=["tests.specs:test_foo"],
    )
    h = format_header(**original)
    parsed = parse_header(h)
    assert parsed["kind"] == "test"
    assert parsed["source_module"] == "tests.specs"
    assert parsed["module_digest"] == "sha256:deadbeef"


def test_parse_header_with_trailing_code():
    """Header followed by actual code should still parse."""
    h = format_header(
        tool_version="0.1.0",
        kind="build",
        source_module="pkg.mod",
        module_digest="sha256:aaa",
        spec_refs=["pkg.mod:fn"],
    )
    full_source = h + "\n\ndef fn():\n    return 42\n"
    parsed = parse_header(full_source)
    assert parsed["module_digest"] == "sha256:aaa"


def test_extract_module_digest():
    h = format_header(
        tool_version="0.1.0",
        kind="build",
        source_module="pkg.mod",
        module_digest="sha256:abc123def",
        spec_refs=[],
    )
    assert extract_module_digest(h) == "sha256:abc123def"


def test_parse_header_returns_none_for_non_jaunt_file():
    assert parse_header("# just a normal python file\nx = 1\n") is None


def test_header_lines_are_comments():
    """Every line in the header must be a Python comment."""
    h = format_header(
        tool_version="0.1.0",
        kind="build",
        source_module="pkg",
        module_digest="sha256:x",
        spec_refs=[],
    )
    for line in h.strip().splitlines():
        assert line.startswith("#"), f"Header line is not a comment: {line}"
```

---

## Phase 1b: Core Data Structures (L1)

### T5 — `tests/test_registry.py`

```python
"""Tests for jaunt/registry.py — global spec registries."""

import pytest
from jaunt.registry import (
    SpecEntry,
    register_magic,
    register_test,
    get_magic_registry,
    get_test_registry,
    get_specs_by_module,
    clear_registries,
)


@pytest.fixture(autouse=True)
def _clean_registry():
    """Ensure tests don't leak state."""
    clear_registries()
    yield
    clear_registries()


def _make_entry(spec_ref, module, qualname, kind="magic"):
    return SpecEntry(
        spec_ref=spec_ref,
        func_or_class=lambda: None,
        module=module,
        qualname=qualname,
        source_file=f"/fake/{module.replace('.', '/')}.py",
        decorator_kwargs={},
        kind=kind,
    )


def test_register_and_retrieve_magic():
    entry = _make_entry("pkg.mod:fn", "pkg.mod", "fn")
    register_magic("pkg.mod:fn", entry)
    assert "pkg.mod:fn" in get_magic_registry()


def test_register_and_retrieve_test():
    entry = _make_entry("tests.spec:test_fn", "tests.spec", "test_fn", kind="test")
    register_test("tests.spec:test_fn", entry)
    assert "tests.spec:test_fn" in get_test_registry()


def test_magic_and_test_registries_are_separate():
    e1 = _make_entry("pkg:fn", "pkg", "fn", kind="magic")
    e2 = _make_entry("tests:t", "tests", "t", kind="test")
    register_magic("pkg:fn", e1)
    register_test("tests:t", e2)
    assert "pkg:fn" not in get_test_registry()
    assert "tests:t" not in get_magic_registry()


def test_clear_registries():
    register_magic("pkg:fn", _make_entry("pkg:fn", "pkg", "fn"))
    clear_registries()
    assert len(get_magic_registry()) == 0
    assert len(get_test_registry()) == 0


def test_get_specs_by_module():
    e1 = _make_entry("pkg.a:fn1", "pkg.a", "fn1")
    e2 = _make_entry("pkg.a:fn2", "pkg.a", "fn2")
    e3 = _make_entry("pkg.b:fn3", "pkg.b", "fn3")
    register_magic("pkg.a:fn1", e1)
    register_magic("pkg.a:fn2", e2)
    register_magic("pkg.b:fn3", e3)
    by_mod = get_specs_by_module("magic")
    assert len(by_mod["pkg.a"]) == 2
    assert len(by_mod["pkg.b"]) == 1


def test_duplicate_registration_overwrites():
    e1 = _make_entry("pkg:fn", "pkg", "fn")
    e2 = _make_entry("pkg:fn", "pkg", "fn")
    e2.decorator_kwargs = {"prompt": "new"}
    register_magic("pkg:fn", e1)
    register_magic("pkg:fn", e2)
    assert get_magic_registry()["pkg:fn"].decorator_kwargs == {"prompt": "new"}
```

---

### T6 — `tests/test_config.py`

```python
"""Tests for jaunt/config.py — parse jaunt.toml."""

import pytest
from pathlib import Path
from jaunt.config import load_config, find_project_root, JauntConfig
from jaunt.errors import JauntConfigError


def test_load_minimal_config(tmp_path):
    (tmp_path / "jaunt.toml").write_text('version = 1\n')
    cfg = load_config(path=tmp_path / "jaunt.toml", root=tmp_path)
    assert isinstance(cfg, JauntConfig)


def test_defaults_applied(tmp_path):
    (tmp_path / "jaunt.toml").write_text('version = 1\n')
    cfg = load_config(path=tmp_path / "jaunt.toml", root=tmp_path)
    assert cfg.paths.generated_dir == "__generated__"
    assert cfg.build.infer_deps is True
    assert cfg.llm.provider == "openai"
    assert cfg.llm.temperature == 0.2


def test_custom_values_override_defaults(tmp_path):
    toml = '''
version = 1

[llm]
model = "gpt-4o"
temperature = 0.5

[build]
jobs = 2
infer_deps = false
'''
    (tmp_path / "jaunt.toml").write_text(toml)
    cfg = load_config(path=tmp_path / "jaunt.toml", root=tmp_path)
    assert cfg.llm.model == "gpt-4o"
    assert cfg.llm.temperature == 0.5
    assert cfg.build.jobs == 2
    assert cfg.build.infer_deps is False


def test_missing_config_raises(tmp_path):
    with pytest.raises(JauntConfigError):
        load_config(path=tmp_path / "nonexistent.toml", root=tmp_path)


def test_invalid_toml_raises(tmp_path):
    (tmp_path / "jaunt.toml").write_text("this is [[[not valid toml")
    with pytest.raises(JauntConfigError):
        load_config(path=tmp_path / "jaunt.toml", root=tmp_path)


def test_find_project_root(tmp_path):
    project = tmp_path / "a" / "b" / "c"
    project.mkdir(parents=True)
    (tmp_path / "a" / "jaunt.toml").write_text('version = 1\n')
    root = find_project_root(start=project)
    assert root == tmp_path / "a"


def test_find_project_root_not_found(tmp_path):
    with pytest.raises(JauntConfigError, match="jaunt.toml"):
        find_project_root(start=tmp_path)
```

---

## Phase 2: Runtime + Discovery (L2)

### T7 — `tests/test_magic_decorator.py`

```python
"""Tests for jaunt/runtime.py — @magic decorator."""

import pytest
from jaunt.runtime import magic
from jaunt.registry import get_magic_registry, clear_registries
from jaunt.errors import JauntNotBuiltError


@pytest.fixture(autouse=True)
def _clean():
    clear_registries()
    yield
    clear_registries()


def test_magic_registers_function():
    @magic()
    def cowsay(text: str) -> str:
        """Make a cow say text."""

    assert any("cowsay" in ref for ref in get_magic_registry())


def test_magic_registers_class():
    @magic()
    class Greeter:
        """A friendly greeter."""

    assert any("Greeter" in ref for ref in get_magic_registry())


def test_magic_function_raises_not_built():
    @magic()
    def unbuilt_fn(x: int) -> int:
        """Double x."""

    with pytest.raises(JauntNotBuiltError, match="jaunt build"):
        unbuilt_fn(5)


def test_magic_class_raises_not_built():
    @magic()
    class UnbuiltClass:
        """Not built yet."""

    with pytest.raises(JauntNotBuiltError):
        UnbuiltClass()


def test_magic_preserves_name():
    @magic()
    def my_func():
        """Docstring."""

    # The wrapper should still expose the original name
    assert "my_func" in repr(my_func) or my_func.__name__ == "my_func" or hasattr(my_func, "__wrapped__")


def test_magic_with_explicit_deps():
    @magic()
    def dep_fn() -> str:
        """A dependency."""

    @magic(deps=[dep_fn])
    def main_fn() -> str:
        """Depends on dep_fn."""

    registry = get_magic_registry()
    main_ref = [r for r in registry if "main_fn" in r][0]
    entry = registry[main_ref]
    assert entry.decorator_kwargs.get("deps") is not None


def test_magic_with_string_deps():
    @magic(deps=["other.module:helper"])
    def my_fn() -> str:
        """Uses helper from another module."""

    registry = get_magic_registry()
    ref = [r for r in registry if "my_fn" in r][0]
    assert "other.module:helper" in str(registry[ref].decorator_kwargs["deps"])


def test_magic_with_prompt():
    @magic(prompt="Use recursion, not iteration")
    def fibonacci(n: int) -> int:
        """Return nth fibonacci number."""

    registry = get_magic_registry()
    ref = [r for r in registry if "fibonacci" in r][0]
    assert registry[ref].decorator_kwargs["prompt"] == "Use recursion, not iteration"
```

---

### T8 — `tests/test_test_decorator.py`

```python
"""Tests for jaunt/runtime.py — @test decorator."""

import pytest
from jaunt.runtime import test
from jaunt.registry import get_test_registry, clear_registries


@pytest.fixture(autouse=True)
def _clean():
    clear_registries()
    yield
    clear_registries()


def test_test_registers_function():
    @test()
    def test_cowsay():
        """Test that cowsay works."""

    assert any("test_cowsay" in ref for ref in get_test_registry())


def test_test_sets_dunder_test_false():
    @test()
    def test_something():
        """Should not be collected by pytest."""

    assert test_something.__test__ is False


def test_test_returns_function_unchanged():
    def original():
        return 42

    decorated = test()(original)
    # The actual callable should still work
    assert decorated() == 42


def test_test_not_in_magic_registry():
    @test()
    def test_fn():
        """A test spec."""

    from jaunt.registry import get_magic_registry
    assert len(get_magic_registry()) == 0


def test_test_with_deps():
    @test(deps=["my_project.foo:cowsay"])
    def test_cowsay():
        """Test cowsay output."""

    registry = get_test_registry()
    ref = [r for r in registry if "test_cowsay" in r][0]
    assert registry[ref].decorator_kwargs.get("deps") is not None
```

---

### T9 — `tests/test_discovery.py`

```python
"""Tests for jaunt/discovery.py — module scanning + import."""

import pytest
from pathlib import Path
from jaunt.discovery import discover_modules, import_and_collect
from jaunt.errors import JauntDiscoveryError
from jaunt.registry import clear_registries


@pytest.fixture(autouse=True)
def _clean():
    clear_registries()
    yield
    clear_registries()


def _make_package(tmp_path, structure: dict[str, str]):
    """Create a fake Python package from a dict of {relative_path: content}."""
    for rel_path, content in structure.items():
        p = tmp_path / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)


def test_discover_finds_py_files(tmp_path):
    _make_package(tmp_path, {
        "pkg/__init__.py": "",
        "pkg/foo.py": "x = 1",
        "pkg/bar.py": "y = 2",
    })
    modules = discover_modules(
        roots=[tmp_path],
        exclude=[],
        generated_dir="__generated__",
    )
    module_names = [m for m in modules if "pkg" in m]
    assert len(module_names) >= 2  # foo and bar at minimum


def test_discover_excludes_generated_dir(tmp_path):
    _make_package(tmp_path, {
        "pkg/__init__.py": "",
        "pkg/foo.py": "x = 1",
        "pkg/__generated__/__init__.py": "",
        "pkg/__generated__/foo.py": "generated = True",
    })
    modules = discover_modules(
        roots=[tmp_path],
        exclude=[],
        generated_dir="__generated__",
    )
    assert not any("__generated__" in m for m in modules)


def test_discover_excludes_glob_patterns(tmp_path):
    _make_package(tmp_path, {
        "pkg/__init__.py": "",
        "pkg/foo.py": "x = 1",
        ".venv/lib/thing.py": "y = 1",
    })
    modules = discover_modules(
        roots=[tmp_path],
        exclude=["**/.venv/**"],
        generated_dir="__generated__",
    )
    assert not any(".venv" in m for m in modules)


def test_discover_returns_sorted(tmp_path):
    _make_package(tmp_path, {
        "pkg/__init__.py": "",
        "pkg/z_mod.py": "",
        "pkg/a_mod.py": "",
    })
    modules = discover_modules(
        roots=[tmp_path],
        exclude=[],
        generated_dir="__generated__",
    )
    pkg_modules = [m for m in modules if "pkg" in m]
    assert pkg_modules == sorted(pkg_modules)


def test_import_error_wraps_in_discovery_error(tmp_path, monkeypatch):
    """A module with a syntax error should raise JauntDiscoveryError."""
    _make_package(tmp_path, {
        "bad_pkg/__init__.py": "this is not valid python !!!",
    })
    import sys
    monkeypatch.syspath_prepend(str(tmp_path))
    # Clean up if already imported
    sys.modules.pop("bad_pkg", None)

    with pytest.raises(JauntDiscoveryError) as exc_info:
        import_and_collect(["bad_pkg"], kind="magic")
    assert "bad_pkg" in str(exc_info.value)
```

---

## Phase 3a: Dependency Graph (L3)

### T10 — `tests/test_deps.py`

```python
"""Tests for jaunt/deps.py — dependency graph building + topo sort."""

import pytest
from jaunt.deps import (
    resolve_explicit_deps,
    build_dependency_graph,
    compute_module_dag,
    topological_sort,
)
from jaunt.errors import JauntDependencyCycleError
from jaunt.registry import SpecEntry


def _entry(spec_ref, module, qualname, deps=None):
    return SpecEntry(
        spec_ref=spec_ref,
        func_or_class=lambda: None,
        module=module,
        qualname=qualname,
        source_file=f"/fake/{module.replace('.', '/')}.py",
        decorator_kwargs={"deps": deps or []},
        kind="magic",
    )


def test_resolve_no_deps():
    entry = _entry("pkg:fn", "pkg", "fn")
    all_specs = {"pkg:fn": entry}
    assert resolve_explicit_deps(entry, all_specs) == set()


def test_resolve_string_deps():
    dep = _entry("pkg:helper", "pkg", "helper")
    main = _entry("pkg:main", "pkg", "main", deps=["pkg:helper"])
    all_specs = {"pkg:helper": dep, "pkg:main": main}
    resolved = resolve_explicit_deps(main, all_specs)
    assert "pkg:helper" in resolved


def test_build_graph_explicit():
    a = _entry("pkg:a", "pkg", "a")
    b = _entry("pkg:b", "pkg", "b", deps=["pkg:a"])
    specs = {"pkg:a": a, "pkg:b": b}
    graph = build_dependency_graph(specs, infer=False)
    assert "pkg:a" in graph["pkg:b"]
    assert len(graph["pkg:a"]) == 0


def test_topological_sort_simple():
    graph = {
        "a": {"b", "c"},  # a depends on b and c
        "b": {"c"},        # b depends on c
        "c": set(),        # c has no deps
    }
    order = topological_sort(graph)
    assert order.index("c") < order.index("b")
    assert order.index("b") < order.index("a")


def test_topological_sort_independent():
    graph = {"a": set(), "b": set(), "c": set()}
    order = topological_sort(graph)
    assert set(order) == {"a", "b", "c"}


def test_topological_sort_cycle_raises():
    graph = {
        "a": {"b"},
        "b": {"c"},
        "c": {"a"},
    }
    with pytest.raises(JauntDependencyCycleError) as exc_info:
        topological_sort(graph)
    # Should mention the cycle participants
    msg = str(exc_info.value)
    assert "a" in msg or "b" in msg or "c" in msg


def test_compute_module_dag():
    """Spec-level edges collapse into module-level edges."""
    a = _entry("mod_a:fn1", "mod_a", "fn1")
    b = _entry("mod_b:fn2", "mod_b", "fn2", deps=["mod_a:fn1"])
    specs = {"mod_a:fn1": a, "mod_b:fn2": b}
    spec_graph = build_dependency_graph(specs, infer=False)
    mod_dag = compute_module_dag(spec_graph)
    assert "mod_a" in mod_dag["mod_b"]


def test_module_dag_no_self_edges():
    """Two specs in the same module depending on each other = no module self-edge."""
    a = _entry("pkg:a", "pkg", "a")
    b = _entry("pkg:b", "pkg", "b", deps=["pkg:a"])
    specs = {"pkg:a": a, "pkg:b": b}
    spec_graph = build_dependency_graph(specs, infer=False)
    mod_dag = compute_module_dag(spec_graph)
    assert "pkg" not in mod_dag.get("pkg", set())
```

---

### T12 — `tests/test_digest.py`

```python
"""Tests for jaunt/digest.py — checksum computation."""

import pytest
from jaunt.digest import local_digest, graph_digest, module_digest
from jaunt.registry import SpecEntry


def _entry(spec_ref, module, qualname, source_file, deps=None):
    return SpecEntry(
        spec_ref=spec_ref,
        func_or_class=lambda: None,
        module=module,
        qualname=qualname,
        source_file=source_file,
        decorator_kwargs={"deps": deps or []},
        kind="magic",
    )


def test_local_digest_is_hex_string(tmp_path):
    src = tmp_path / "mod.py"
    src.write_text("def foo():\n    '''Do something.'''\n    pass\n")
    entry = _entry("mod:foo", "mod", "foo", str(src))
    d = local_digest(entry)
    assert isinstance(d, str)
    assert len(d) == 64  # sha256 hex


def test_local_digest_deterministic(tmp_path):
    src = tmp_path / "mod.py"
    src.write_text("def foo():\n    '''Do something.'''\n    pass\n")
    entry = _entry("mod:foo", "mod", "foo", str(src))
    assert local_digest(entry) == local_digest(entry)


def test_local_digest_changes_on_source_change(tmp_path):
    src = tmp_path / "mod.py"
    src.write_text("def foo():\n    '''Version 1.'''\n    pass\n")
    entry = _entry("mod:foo", "mod", "foo", str(src))
    d1 = local_digest(entry)

    src.write_text("def foo():\n    '''Version 2.'''\n    pass\n")
    d2 = local_digest(entry)
    assert d1 != d2


def test_graph_digest_no_deps(tmp_path):
    src = tmp_path / "mod.py"
    src.write_text("def foo():\n    pass\n")
    entry = _entry("mod:foo", "mod", "foo", str(src))
    specs = {"mod:foo": entry}
    graph = {"mod:foo": set()}
    d = graph_digest("mod:foo", specs, graph, cache={})
    assert isinstance(d, str) and len(d) == 64


def test_graph_digest_changes_when_dep_changes(tmp_path):
    src = tmp_path / "mod.py"
    src.write_text("def a():\n    '''V1.'''\n    pass\n\ndef b():\n    pass\n")
    a = _entry("mod:a", "mod", "a", str(src))
    b = _entry("mod:b", "mod", "b", str(src), deps=["mod:a"])
    specs = {"mod:a": a, "mod:b": b}
    graph = {"mod:a": set(), "mod:b": {"mod:a"}}

    d1 = graph_digest("mod:b", specs, graph, cache={})

    # Change a's source
    src.write_text("def a():\n    '''V2 changed.'''\n    pass\n\ndef b():\n    pass\n")
    d2 = graph_digest("mod:b", specs, graph, cache={})
    assert d1 != d2


def test_module_digest_aggregates_specs(tmp_path):
    src = tmp_path / "mod.py"
    src.write_text("def a():\n    pass\n\ndef b():\n    pass\n")
    a = _entry("mod:a", "mod", "a", str(src))
    b = _entry("mod:b", "mod", "b", str(src))
    specs = {"mod:a": a, "mod:b": b}
    graph = {"mod:a": set(), "mod:b": set()}
    d = module_digest("mod", [a, b], specs, graph)
    assert isinstance(d, str) and len(d) == 64
```

---

## Phase 3b: Code Generation Backend (L4, parallel with L3)

### T13 — `tests/test_base_backend.py`

```python
"""Tests for jaunt/base.py — backend interface + data structures."""

from jaunt.base import ModuleSpecContext, GeneratorBackend, GenerationResult


def test_module_spec_context_creation():
    ctx = ModuleSpecContext(
        module_name="pkg.mod",
        kind="build",
        spec_entries=[],
        spec_sources={},
        dependency_apis={},
        dependency_generated_code={},
    )
    assert ctx.module_name == "pkg.mod"
    assert ctx.kind == "build"


def test_generation_result_success():
    r = GenerationResult(module_name="pkg.mod", source="def fn(): pass", success=True, error=None)
    assert r.success


def test_generation_result_failure():
    r = GenerationResult(module_name="pkg.mod", source="", success=False, error="LLM timeout")
    assert not r.success
    assert "timeout" in r.error


def test_generator_backend_is_abstract():
    """Cannot instantiate GeneratorBackend directly."""
    import pytest
    with pytest.raises(TypeError):
        GeneratorBackend()
```

---

### T15 — `tests/test_validation.py`

```python
"""Tests for jaunt/validation.py — output validation utilities."""

from jaunt.validation import validate_generated_source, compile_check


def test_valid_source_with_all_names():
    source = "def foo():\n    return 1\n\ndef bar():\n    return 2\n"
    missing = validate_generated_source(source, expected_names=["foo", "bar"])
    assert missing == []


def test_missing_name_detected():
    source = "def foo():\n    return 1\n"
    missing = validate_generated_source(source, expected_names=["foo", "bar"])
    assert "bar" in missing


def test_syntax_error_detected():
    source = "def foo(:\n    return 1\n"
    errors = validate_generated_source(source, expected_names=["foo"])
    assert len(errors) > 0
    assert any("syntax" in e.lower() or "SyntaxError" in e for e in errors)


def test_class_names_detected():
    source = "class MyClass:\n    pass\n"
    missing = validate_generated_source(source, expected_names=["MyClass"])
    assert missing == []


def test_compile_check_valid():
    assert compile_check("x = 1\n", "test.py") is True


def test_compile_check_invalid():
    assert compile_check("def (broken\n", "test.py") is False


def test_empty_source_valid_if_no_names_expected():
    missing = validate_generated_source("", expected_names=[])
    # Empty source is technically parseable
    assert missing == []


def test_assignment_names_detected():
    """Top-level assignments like `CONSTANT = 42` count as defined names."""
    source = "TIMEOUT = 30\n"
    missing = validate_generated_source(source, expected_names=["TIMEOUT"])
    assert missing == []
```

---

### T14 — `tests/test_openai_backend.py`

```python
"""Tests for jaunt/openai_backend.py — OpenAI backend (mocked)."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from jaunt.openai_backend import OpenAIBackend
from jaunt.base import ModuleSpecContext
from jaunt.config import LLMConfig


@pytest.fixture
def llm_config():
    return LLMConfig(
        provider="openai",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        base_url="https://api.openai.com/v1",
        timeout_s=30,
        temperature=0.2,
    )


@pytest.fixture
def simple_context():
    return ModuleSpecContext(
        module_name="pkg.mod",
        kind="build",
        spec_entries=[],
        spec_sources={"pkg.mod:foo": "def foo():\n    '''Return 42.'''\n    pass\n"},
        dependency_apis={},
        dependency_generated_code={},
    )


def test_backend_instantiates(llm_config, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    backend = OpenAIBackend(llm_config)
    assert backend is not None


@pytest.mark.asyncio
async def test_backend_extracts_code_from_fenced_response(llm_config, simple_context, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    backend = OpenAIBackend(llm_config)

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "```python\ndef foo():\n    return 42\n```"

    with patch.object(backend._client.chat.completions, "create", new_callable=AsyncMock, return_value=mock_response):
        result = await backend.generate_module(simple_context)

    assert "def foo():" in result
    assert "```" not in result  # Fences stripped


@pytest.mark.asyncio
async def test_backend_build_prompt_excludes_tests(llm_config, simple_context, monkeypatch):
    """Build prompts must not mention generating tests."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    backend = OpenAIBackend(llm_config)

    captured_messages = None
    async def capture_create(**kwargs):
        nonlocal captured_messages
        captured_messages = kwargs.get("messages", [])
        mock = MagicMock()
        mock.choices = [MagicMock()]
        mock.choices[0].message.content = "def foo():\n    return 42\n"
        return mock

    with patch.object(backend._client.chat.completions, "create", side_effect=capture_create):
        await backend.generate_module(simple_context)

    full_prompt = str(captured_messages)
    assert "test" not in full_prompt.lower() or "do not" in full_prompt.lower()
```

---

## Phase 4: Orchestration (L5-L6)

### T16 + T17 — `tests/test_builder_io.py`

```python
"""Tests for jaunt/builder.py — file writing + staleness detection."""

import pytest
from pathlib import Path
from jaunt.builder import write_generated_module, detect_stale_modules
from jaunt.header import parse_header
from jaunt.registry import SpecEntry


def _entry(spec_ref, module, qualname, source_file, deps=None):
    return SpecEntry(
        spec_ref=spec_ref,
        func_or_class=lambda: None,
        module=module,
        qualname=qualname,
        source_file=source_file,
        decorator_kwargs={"deps": deps or []},
        kind="magic",
    )


def test_write_creates_file(tmp_path):
    out = write_generated_module(
        package_dir=tmp_path / "pkg",
        generated_dir="__generated__",
        module_name="pkg.foo",
        source="def foo():\n    return 42\n",
        header_fields={
            "tool_version": "0.1.0",
            "kind": "build",
            "source_module": "pkg.foo",
            "module_digest": "sha256:abc",
            "spec_refs": ["pkg.foo:foo"],
        },
    )
    assert out.exists()
    content = out.read_text()
    assert "DO NOT EDIT" in content
    assert "def foo():" in content


def test_write_creates_init_files(tmp_path):
    """Intermediate __init__.py files should be created."""
    write_generated_module(
        package_dir=tmp_path / "pkg",
        generated_dir="__generated__",
        module_name="pkg.sub.mod",
        source="x = 1\n",
        header_fields={
            "tool_version": "0.1.0",
            "kind": "build",
            "source_module": "pkg.sub.mod",
            "module_digest": "sha256:abc",
            "spec_refs": [],
        },
    )
    gen_init = tmp_path / "pkg" / "__generated__" / "__init__.py"
    assert gen_init.exists()


def test_write_is_atomic(tmp_path):
    """If we write the same path twice, no partial files should be visible."""
    for i in range(2):
        write_generated_module(
            package_dir=tmp_path / "pkg",
            generated_dir="__generated__",
            module_name="pkg.foo",
            source=f"VERSION = {i}\n",
            header_fields={
                "tool_version": "0.1.0",
                "kind": "build",
                "source_module": "pkg.foo",
                "module_digest": f"sha256:v{i}",
                "spec_refs": [],
            },
        )
    content = (tmp_path / "pkg" / "__generated__" / "foo.py").read_text()
    assert "VERSION = 1" in content


def test_staleness_missing_file(tmp_path):
    """Module with no generated file is stale."""
    src = tmp_path / "mod.py"
    src.write_text("def fn():\n    pass\n")
    entry = _entry("mod:fn", "mod", "fn", str(src))
    stale = detect_stale_modules(
        module_specs={"mod": [entry]},
        graph={"mod:fn": set()},
        package_dir=tmp_path,
        generated_dir="__generated__",
        force=False,
    )
    assert "mod" in stale


def test_staleness_force_always_stale(tmp_path):
    """--force marks everything stale even if digests match."""
    src = tmp_path / "mod.py"
    src.write_text("def fn():\n    pass\n")
    entry = _entry("mod:fn", "mod", "fn", str(src))

    # Write a generated file (with any digest)
    write_generated_module(
        package_dir=tmp_path,
        generated_dir="__generated__",
        module_name="mod",
        source="def fn():\n    return 1\n",
        header_fields={
            "tool_version": "0.1.0",
            "kind": "build",
            "source_module": "mod",
            "module_digest": "sha256:matching",
            "spec_refs": ["mod:fn"],
        },
    )
    stale = detect_stale_modules(
        module_specs={"mod": [entry]},
        graph={"mod:fn": set()},
        package_dir=tmp_path,
        generated_dir="__generated__",
        force=True,
    )
    assert "mod" in stale
```

---

### T18 — `tests/test_build_scheduler.py`

```python
"""Tests for jaunt/builder.py — parallel build scheduler with FakeBackend."""

import pytest
import asyncio
from jaunt.base import ModuleSpecContext, GeneratorBackend
from jaunt.builder import run_build
from jaunt.registry import SpecEntry


class FakeBackend(GeneratorBackend):
    """Returns deterministic code for any module."""

    def __init__(self):
        self.call_count = 0
        self.modules_generated = []

    async def generate_module(self, context: ModuleSpecContext) -> str:
        self.call_count += 1
        self.modules_generated.append(context.module_name)
        # Generate a simple valid module with all expected names
        defs = []
        for ref, src in context.spec_sources.items():
            name = ref.split(":")[-1]
            defs.append(f"def {name}():\n    return '{name}_impl'\n")
        return "\n".join(defs)


def _entry(spec_ref, module, qualname, source_file, deps=None):
    return SpecEntry(
        spec_ref=spec_ref,
        func_or_class=lambda: None,
        module=module,
        qualname=qualname,
        source_file=source_file,
        decorator_kwargs={"deps": deps or []},
        kind="magic",
    )


@pytest.mark.asyncio
async def test_build_generates_all_stale(tmp_path):
    src = tmp_path / "src" / "pkg"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text("")
    (src / "mod.py").write_text("def foo():\n    '''Do foo.'''\n    pass\n")

    entry = _entry("pkg.mod:foo", "pkg.mod", "foo", str(src / "mod.py"))
    backend = FakeBackend()

    report = await run_build(
        config=None,  # not needed by FakeBackend
        specs={"pkg.mod": [entry]},
        graph={"pkg.mod:foo": set()},
        module_dag={"pkg.mod": set()},
        stale_modules={"pkg.mod"},
        backend=backend,
        jobs=2,
        package_dir=src.parent,
        generated_dir="__generated__",
    )
    assert "pkg.mod" in report.generated
    assert backend.call_count == 1


@pytest.mark.asyncio
async def test_build_respects_dependency_order(tmp_path):
    src = tmp_path / "src" / "pkg"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text("")
    (src / "a.py").write_text("def a_fn():\n    pass\n")
    (src / "b.py").write_text("def b_fn():\n    pass\n")

    a = _entry("pkg.a:a_fn", "pkg.a", "a_fn", str(src / "a.py"))
    b = _entry("pkg.b:b_fn", "pkg.b", "b_fn", str(src / "b.py"), deps=["pkg.a:a_fn"])

    backend = FakeBackend()

    report = await run_build(
        config=None,
        specs={"pkg.a": [a], "pkg.b": [b]},
        graph={"pkg.a:a_fn": set(), "pkg.b:b_fn": {"pkg.a:a_fn"}},
        module_dag={"pkg.a": set(), "pkg.b": {"pkg.a"}},
        stale_modules={"pkg.a", "pkg.b"},
        backend=backend,
        jobs=1,
        package_dir=src.parent,
        generated_dir="__generated__",
    )
    # a must be generated before b
    assert backend.modules_generated.index("pkg.a") < backend.modules_generated.index("pkg.b")


@pytest.mark.asyncio
async def test_build_skips_non_stale(tmp_path):
    src = tmp_path / "pkg"
    src.mkdir(parents=True)
    (src / "mod.py").write_text("def foo():\n    pass\n")

    entry = _entry("pkg.mod:foo", "pkg.mod", "foo", str(src / "mod.py"))
    backend = FakeBackend()

    report = await run_build(
        config=None,
        specs={"pkg.mod": [entry]},
        graph={"pkg.mod:foo": set()},
        module_dag={"pkg.mod": set()},
        stale_modules=set(),  # nothing stale
        backend=backend,
        jobs=2,
        package_dir=tmp_path,
        generated_dir="__generated__",
    )
    assert backend.call_count == 0
    assert "pkg.mod" in report.skipped
```

---

### T20 — `tests/test_pytest_runner.py`

```python
"""Tests for jaunt/tester.py — pytest runner."""

import pytest
from pathlib import Path
from jaunt.tester import run_pytest


def test_run_pytest_on_passing_tests(tmp_path):
    test_file = tmp_path / "test_ok.py"
    test_file.write_text("def test_passes():\n    assert 1 + 1 == 2\n")
    exit_code = run_pytest([test_file], pytest_args=["-q", "--no-header"])
    assert exit_code == 0


def test_run_pytest_on_failing_tests(tmp_path):
    test_file = tmp_path / "test_fail.py"
    test_file.write_text("def test_fails():\n    assert False\n")
    exit_code = run_pytest([test_file], pytest_args=["-q", "--no-header"])
    assert exit_code != 0


def test_run_pytest_multiple_files(tmp_path):
    f1 = tmp_path / "test_a.py"
    f1.write_text("def test_a():\n    assert True\n")
    f2 = tmp_path / "test_b.py"
    f2.write_text("def test_b():\n    assert True\n")
    exit_code = run_pytest([f1, f2], pytest_args=["-q"])
    assert exit_code == 0


def test_run_pytest_empty_file_list():
    """No files = nothing to run = success (or pytest's no-tests exit code)."""
    exit_code = run_pytest([], pytest_args=["-q"])
    assert exit_code in (0, 5)  # 5 = pytest "no tests collected"
```

---

## Phase 5: CLI (L7)

### T21-T23 — `tests/test_cli.py`

```python
"""Tests for jaunt/cli.py — CLI argument parsing + subcommands."""

import pytest
from unittest.mock import patch, AsyncMock
from jaunt.cli import main, parse_args


def test_parse_build_defaults():
    args = parse_args(["build"])
    assert args.command == "build"
    assert args.force is False
    assert args.target == []


def test_parse_build_with_flags():
    args = parse_args(["build", "--force", "--jobs", "4", "--target", "pkg.mod:fn"])
    assert args.force is True
    assert args.jobs == 4
    assert "pkg.mod:fn" in args.target


def test_parse_build_no_infer_deps():
    args = parse_args(["build", "--no-infer-deps"])
    assert args.no_infer_deps is True


def test_parse_test_defaults():
    args = parse_args(["test"])
    assert args.command == "test"
    assert args.no_build is False
    assert args.no_run is False


def test_parse_test_with_flags():
    args = parse_args(["test", "--no-build", "--no-run", "--pytest-args", "-v"])
    assert args.no_build is True
    assert args.no_run is True


def test_parse_no_command_shows_help(capsys):
    with pytest.raises(SystemExit):
        parse_args([])


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as exc_info:
        parse_args(["--version"])
    assert exc_info.value.code == 0


def test_build_exit_code_0_on_success(tmp_path):
    """End-to-end: jaunt build on a trivial project with FakeBackend."""
    (tmp_path / "jaunt.toml").write_text('version = 1\n')
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("")

    with patch("jaunt.cli.cmd_build", return_value=0) as mock:
        result = main(["build", "--root", str(tmp_path)])
    assert result == 0


def test_build_exit_code_2_on_config_error(tmp_path):
    """Missing jaunt.toml should exit 2."""
    with patch("jaunt.cli.cmd_build", return_value=2):
        result = main(["build", "--root", str(tmp_path)])
    assert result == 2
```

---

## Phase 6: Integration (L-test)

### `tests/test_integration.py`

```python
"""End-to-end integration tests using FakeBackend and tmp_path projects."""

import pytest
from pathlib import Path


def _create_project(tmp_path) -> Path:
    """Create a minimal Jaunt project."""
    root = tmp_path / "project"
    root.mkdir()

    (root / "jaunt.toml").write_text("""
version = 1

[paths]
source_roots = ["src"]
test_roots = ["tests"]
""")

    # Source package
    src = root / "src" / "mylib"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text("""
import jaunt

@jaunt.magic()
def greet(name: str) -> str:
    \"\"\"Return a greeting for the given name.
    
    Example: greet("World") -> "Hello, World!"
    \"\"\"
    pass
""")

    # Test specs
    tests = root / "tests"
    tests.mkdir()
    (tests / "__init__.py").write_text("""
import jaunt
from mylib import greet

@jaunt.test(deps=[greet])
def test_greet():
    \"\"\"Test that greet returns proper greeting string.
    Verify: greet("World") == "Hello, World!"
    Verify: greet("") handles empty string gracefully.
    \"\"\"
    pass
""")

    return root


def test_project_structure_created(tmp_path):
    root = _create_project(tmp_path)
    assert (root / "jaunt.toml").exists()
    assert (root / "src" / "mylib" / "__init__.py").exists()
    assert (root / "tests" / "__init__.py").exists()


def test_specs_discoverable(tmp_path):
    """Import the project and verify specs are registered."""
    root = _create_project(tmp_path)
    import sys
    sys.path.insert(0, str(root / "src"))
    try:
        from jaunt.registry import clear_registries, get_magic_registry
        clear_registries()
        import importlib
        import mylib
        importlib.reload(mylib)
        registry = get_magic_registry()
        assert any("greet" in ref for ref in registry)
    finally:
        sys.path.remove(str(root / "src"))
        sys.modules.pop("mylib", None)
        from jaunt.registry import clear_registries
        clear_registries()


# Future: test full build + test cycle with FakeBackend once T18 is done
# def test_full_build_cycle(tmp_path): ...
# def test_full_test_cycle(tmp_path): ...
```

---

## Test Dependency Map (which tests need which implementations)

```
IMPLEMENTATION DONE  →  TESTS YOU CAN NOW WRITE + RUN
─────────────────────────────────────────────────────
(nothing)            →  T1 tests  (just imports)
T1 (errors)          →  T2 tests  (spec_ref)
                     →  T3 tests  (pyproject)
                     →  T4 tests  (header)
T1+T2                →  T5 tests  (registry)
T1                   →  T6 tests  (config)
T1+T2+T5             →  T7 tests  (magic decorator)
                     →  T8 tests  (test decorator)
T1+T5+T6             →  T9 tests  (discovery)
T1+T2+T5             →  T10 tests (deps)
T1+T2+T5+T10         →  T12 tests (digest)
T1+T5                →  T13 tests (base backend)
                     →  T15 tests (validation)
T1+T6+T13            →  T14 tests (openai mocked)
T4+T12+T15           →  T16+T17 tests (builder io)
T13+T16+T17          →  T18 tests (scheduler)
(standalone)         →  T20 tests (pytest runner)
T6                   →  T21-23 tests (cli)
T7+T8+T9             →  integration tests
```

## Running Tests

```bash
# Run all tests for a specific task
uv run pytest tests/test_errors.py -v

# Run all tests up to current phase
uv run pytest tests/test_errors.py tests/test_spec_ref.py tests/test_header.py -v

# Run everything
uv run pytest tests/ -v --tb=short
```
