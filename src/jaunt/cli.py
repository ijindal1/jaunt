from __future__ import annotations

import argparse
import sys

from jaunt import __version__, hello


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jaunt")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    hello_p = subparsers.add_parser("hello", help="Print a greeting")
    hello_p.add_argument("name", nargs="?", help="Name to greet (optional)")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        print(hello())
        return 0

    if args.command == "hello":
        print(hello(args.name))
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

