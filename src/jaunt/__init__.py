from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version


def hello(name: str | None = None) -> str:
    """Return a friendly greeting."""

    if name:
        return f"Hello, {name}!"
    return "Hello from jaunt!"


def _package_version() -> str:
    try:
        return version("jaunt")
    except PackageNotFoundError:
        # Running from a source checkout, or otherwise not installed.
        return "0.0.0"


__version__ = _package_version()

__all__ = ["__version__", "hello"]

