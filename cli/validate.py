"""ATP M1-M2 validate CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.classification.classifier import classify_request
from core.intake.loader import RequestLoadError, load_request
from core.intake.normalizer import normalize_request


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate an ATP M1-M2 request preview.")
    parser.add_argument("request_file", help="Path to a JSON or YAML request file.")
    return parser


def validate_request(request_file: str) -> dict[str, Any]:
    """Load, normalize, and classify a request file."""

    raw_request = load_request(request_file)
    normalized_request = normalize_request(raw_request)
    classification = classify_request(normalized_request)
    return {
        "request_file": request_file,
        "request_id": normalized_request["request_id"],
        "product": normalized_request["product"],
        "request_type": classification["request_type"],
        "execution_intent": classification["execution_intent"],
        "domain": classification["domain"],
    }


def main(argv: list[str] | None = None) -> int:
    """Validate ATP seed request assets."""

    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        summary = validate_request(args.request_file)
    except (RequestLoadError, ValueError) as exc:
        print(
            json.dumps(
                {"status": "error", "error": str(exc), "request_file": args.request_file},
                indent=2,
                sort_keys=True,
            )
        )
        return 1

    print(
        json.dumps(
            {"status": "ok", "summary": summary},
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
