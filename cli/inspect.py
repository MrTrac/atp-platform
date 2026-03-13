"""ATP M1-M2 inspect CLI placeholder."""

from __future__ import annotations

import argparse


def _build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description="Inspect ATP run artifacts.")


def main(argv: list[str] | None = None) -> int:
    """Show the intentional M1-M2 inspect placeholder."""

    _build_parser().parse_args(argv)
    print("ATP inspect is deferred until later milestones. No run inspection logic is implemented in M1-M2.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
