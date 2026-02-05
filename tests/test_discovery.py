from __future__ import annotations

from pathlib import Path

import pytest

from jaunt.discovery import discover_modules, import_and_collect
from jaunt.errors import JauntDiscoveryError


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_discover_modules_finds_pkg_modules(tmp_path: Path) -> None:
    _write(tmp_path / "pkg" / "__init__.py", "")
    _write(tmp_path / "pkg" / "foo.py", "X = 1\n")
    _write(tmp_path / "pkg" / "bar.py", "Y = 2\n")

    mods = discover_modules(roots=[tmp_path], exclude=[], generated_dir="__generated__")

    assert "pkg.foo" in mods
    assert "pkg.bar" in mods
    assert mods == sorted(mods)


def test_discover_modules_excludes_generated_dir(tmp_path: Path) -> None:
    _write(tmp_path / "pkg" / "__init__.py", "")
    _write(tmp_path / "pkg" / "__generated__" / "gen.py", "Z = 3\n")
    _write(tmp_path / "pkg" / "ok.py", "OK = True\n")

    mods = discover_modules(roots=[tmp_path], exclude=[], generated_dir="__generated__")

    assert "pkg.__generated__.gen" not in mods
    assert "pkg.ok" in mods


def test_discover_modules_honors_exclude_globs(tmp_path: Path) -> None:
    _write(tmp_path / "pkg" / "__init__.py", "")
    _write(tmp_path / "pkg" / "ok.py", "OK = True\n")
    _write(tmp_path / ".venv" / "site.py", "NOPE = 1\n")

    mods = discover_modules(
        roots=[tmp_path],
        exclude=["**/.venv/**"],
        generated_dir="__generated__",
    )

    assert "pkg.ok" in mods
    assert ".venv.site" not in mods


def test_import_and_collect_wraps_import_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write(tmp_path / "badmod.py", "def oops(:\n    pass\n")
    monkeypatch.syspath_prepend(str(tmp_path))

    with pytest.raises(JauntDiscoveryError) as excinfo:
        import_and_collect(["badmod"], kind="test")

    assert "badmod" in str(excinfo.value)


def test_import_and_collect_imports_modules(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write(tmp_path / "okmod.py", "VALUE = 123\n")
    monkeypatch.syspath_prepend(str(tmp_path))

    import_and_collect(["okmod"], kind="test")
