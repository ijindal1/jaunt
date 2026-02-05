from __future__ import annotations

from dataclasses import dataclass


# Example: a stateful class spec stub.
#
# @jaunt.magic
@dataclass
class LRUCache:
    """
    A fixed-capacity least-recently-used cache.

    Parameters:
    - capacity: max number of items (>= 1)

    Behavior:
    - get(key) -> value | None
      - Returns None if missing.
      - Marks the key as most-recently-used if present.
    - set(key, value) -> None
      - Inserts/updates the value.
      - If capacity is exceeded, evict the least-recently-used key.
    - size() -> int returns the current number of keys.

    Constraints:
    - All operations should be O(1) average-case.
    """

    capacity: int

    def get(self, key: str) -> object | None:
        """See class docstring."""
        raise NotImplementedError

    def set(self, key: str, value: object) -> None:
        """See class docstring."""
        raise NotImplementedError

    def size(self) -> int:
        """See class docstring."""
        raise NotImplementedError
