#!/usr/bin/env python3
"""Build the loom-pipeline Workflow driver asset.

Concatenates every ``loom-pipeline/scripts/driver_NN_*.js`` module, in
filename order (NN ascending), into ONE self-contained script:

    loom-pipeline/skills/using-loom-pipeline/assets/loom-pipeline.js

That assembled asset is the only thing the Workflow tool ever runs (see
driver_00_header.js's CONCAT CONTRACT). This script prepends a
generated-file banner so nobody hand-edits the assembled output.

Usage:
    python3 loom-pipeline/scripts/build_driver.py
    python3 loom-pipeline/scripts/build_driver.py --out /tmp/loom-pipeline.js

Pure stdlib. Paths resolve relative to this script's own location so it
runs correctly regardless of the caller's cwd.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
PIPELINE_ROOT = SCRIPTS_DIR.parent
DEFAULT_OUT = (
    PIPELINE_ROOT / "skills" / "using-loom-pipeline" / "assets" / "loom-pipeline.js"
)

BANNER = (
    "// GENERATED FILE — do not edit; built by "
    "loom-pipeline/scripts/build_driver.py from driver_NN_*.js sources.\n"
    "// Rebuild: python3 loom-pipeline/scripts/build_driver.py\n\n"
)


def find_driver_sources() -> list[Path]:
    """Return every driver_NN_*.js source, sorted by filename ascending.

    Lexicographic sort == numeric sort ONLY while NN stays 2-digit
    (driver_100 would sort before driver_90) — keep the prefix 2-digit.
    """
    return sorted(SCRIPTS_DIR.glob("driver_*.js"))


def build(out_path: Path) -> None:
    """Concatenate all driver sources (banner-prefixed) into out_path."""
    sources = find_driver_sources()
    if not sources:
        raise SystemExit(
            f"ERROR: no driver_NN_*.js sources found in {SCRIPTS_DIR} — "
            "nothing to build."
        )

    parts = [BANNER]
    for src in sources:
        parts.append(src.read_text(encoding="utf-8"))
        parts.append("\n")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(parts), encoding="utf-8")
    print(f"[build-driver] wrote {out_path} from {len(sources)} source(s):")
    for src in sources:
        print(f"  - {src.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Alternate output path (default: the committed asset path).",
    )
    args = parser.parse_args()
    build(args.out.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
