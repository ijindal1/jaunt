from __future__ import annotations


# Example: a pure function spec stub.
# In a Jaunt workflow, this function would be generated from the spec; do not implement by hand.
#
# @jaunt.magic
def slugify(title: str) -> str:
    """
    Convert a human title to a URL-safe slug.

    Requirements:
    - Lowercase.
    - Trim leading/trailing whitespace.
    - Replace runs of whitespace with a single "-".
    - Remove characters that are not ASCII letters, digits, "-" or "_".
    - Must never produce an empty string:
      - If nothing remains after filtering, raise ValueError.

    Examples:
    - "Hello World" -> "hello-world"
    - "  A  B  " -> "a-b"
    - "C++" -> "c"
    """
    raise NotImplementedError
