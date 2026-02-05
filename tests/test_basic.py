from __future__ import annotations

import jaunt


def test_version_is_string() -> None:
    assert isinstance(jaunt.__version__, str)
