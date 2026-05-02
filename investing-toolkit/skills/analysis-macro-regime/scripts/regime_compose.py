#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
regime_compose.py — analysis-macro-regime Phase 1 dispatcher (Layer 2, pure compute).

Per ADR-0004, this script is a **thin dispatcher**: for each country in
--input, dispatch to the per-country `classify_{country}` module. All 5
classifiers (US/JP/TW/KR/CN) ship in v2.1.0; the v1.9.0 unified
fallback is removed. `cross_country` is hardcoded null in Phase 1 —
Phase 2 (deferred ADR-0005) will design it bottom-up from observed
native_verdict shapes.

Output schema:
  {
    "schema_version": "2.0-phase1",
    "by_country": {
      "us": <CountryRegimeCard>,
      ...
    },
    "cross_country": null,
    "_legacy": null,
    "_provenance": {...}
  }

Pure compute — no network I/O. Imports stdlib + _surface + calibrations
+ (per-country) classify_X. PyYAML required for calibrations.

Usage:
  uv run regime_compose.py --input us=/tmp/us.json,jp=/tmp/jp.json
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Make sibling modules importable when executed as a script
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from _surface import Phase1Output  # noqa: E402

SUPPORTED_COUNTRIES = {"us", "jp", "tw", "kr", "cn"}


def _try_load_classifier(country: str):
    """Return classify_{country} callable if module exists, else None."""
    try:
        module = importlib.import_module(f"classify_{country}")
    except ImportError:
        return None
    return getattr(module, f"classify_{country}", None)


def parse_input_arg(arg: str) -> dict[str, str]:
    """Parse 'us=/tmp/a.json,jp=/tmp/b.json' into {'us': '/tmp/a.json', ...}."""
    out: dict[str, str] = {}
    for chunk in arg.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "=" not in chunk:
            raise SystemExit(f"Bad --input fragment '{chunk}' — expected country=path")
        cc, path = chunk.split("=", 1)
        cc = cc.strip().lower()
        path = path.strip()
        if cc not in SUPPORTED_COUNTRIES:
            raise SystemExit(f"Unknown country '{cc}' — expected us/jp/tw/kr/cn")
        out[cc] = path
    if not out:
        raise SystemExit("--input is empty")
    return out


def load_pack(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="analysis-macro-regime Phase 1 dispatcher (pure compute)",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Comma-separated country=path pairs, e.g. us=/tmp/us.json,jp=/tmp/jp.json",
    )
    args = parser.parse_args()

    inputs = parse_input_arg(args.input)
    output = Phase1Output()
    # _legacy is kept as `null` (per ADR-0004 PR-7 cleanup) so the schema
    # shape stays stable for downstream consumers. The v1.9.0 fallback
    # path was removed once all 5 per-country classifiers shipped.
    output._legacy = None

    for cc, path in inputs.items():
        try:
            pack = load_pack(path)
        except (OSError, json.JSONDecodeError) as e:
            print(f"ERROR loading {cc}={path}: {e}", file=sys.stderr)
            return 2

        classifier = _try_load_classifier(cc)
        if classifier is None:
            # Phase 1 invariant: all 5 classifiers ship in v2.1.0
            output.by_country[cc] = {
                "country": cc,
                "_error": f"classify_{cc} module not found",
                "_note": (
                    f"Phase 1 invariant violation: every supported country "
                    f"must have a classify_{cc} module. Did you delete it?"
                ),
            }
            continue
        try:
            card = classifier(pack)
            output.by_country[cc] = card.to_dict()
        except Exception as e:
            output.by_country[cc] = {
                "country": cc,
                "_error": f"{type(e).__name__}: {e}",
                "_note": f"classify_{cc} raised at runtime",
            }

    # Provenance metadata (carried over from v1.x for downstream readers)
    payload = output.to_dict()
    payload["_provenance"] = {
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "input_countries": sorted(inputs.keys()),
        "skill": "analysis-macro-regime",
        "phase": "1",
    }

    # default=str coerces YAML-loaded date / datetime objects (e.g.
    # calibration provenance dates) to ISO-format strings.
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
