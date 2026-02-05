from __future__ import annotations

import subprocess
import sys

import jaunt


def test_hello_default() -> None:
    assert jaunt.hello() == "Hello from jaunt!"


def test_hello_name() -> None:
    assert jaunt.hello("Ishita") == "Hello, Ishita!"


def test_module_invocation_prints_greeting() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "jaunt"],
        check=False,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    assert "Hello from jaunt!" in proc.stdout


def test_cli_version_flag() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "jaunt", "--version"],
        check=False,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    assert proc.stdout.startswith("jaunt ")

