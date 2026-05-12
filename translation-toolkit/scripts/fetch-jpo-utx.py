#!/usr/bin/env python3
"""Optional fetch: 特許庁 UTX dictionary (~130k EN-JA patent terms).

License: AAMT distributes; "single dead-copy redistribution NOT permitted",
must indicate JPO + INPIT as copyright holders, format-converted derivatives
permitted. Hence: NOT bundled; users fetch + must comply with attribution.

Usage:
  python3 fetch-jpo-utx.py

Cache location:
  ~/.cache/translation-toolkit/jpo-utx/JPO-UTX.utx
"""
from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

CACHE_ROOT = Path.home() / ".cache" / "translation-toolkit" / "jpo-utx"
SOURCE_URL = "https://aamt.info/japanese/jpo/jpo-utx-2017-06.utx"  # verify current URL before publishing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Download 特許庁 UTX patent term dictionary to local cache. Attribution: 特許庁 + INPIT required.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=CACHE_ROOT,
        help=f"Override cache directory (default: {CACHE_ROOT}).",
    )
    args = parser.parse_args(argv)

    args.cache_dir.mkdir(parents=True, exist_ok=True)
    out = args.cache_dir / "JPO-UTX.utx"

    print(f"Downloading {SOURCE_URL}", file=sys.stderr)
    print(f"  -> {out}", file=sys.stderr)

    try:
        urllib.request.urlretrieve(SOURCE_URL, out)
    except Exception as e:
        print(f"ERROR: download failed: {e}", file=sys.stderr)
        return 1

    print(f"OK: downloaded.", file=sys.stderr)
    print(f"NOTE: Attribution required: 特許庁 + INPIT", file=sys.stderr)
    print(f"      Patent-domain terms; not used unless skill is invoked on patent content.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
