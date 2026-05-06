#!/usr/bin/env python3
"""Optional fetch: Microsoft Terminology Collection (~33k entries x 100+ langs).

License: GRAY. Microsoft Learn allows "use to develop localized versions or
integrate into other terminology collections" but does not explicitly license
redistribution. Hence: NOT bundled in plugin; users run this script to download
to their own machine cache.

Usage:
  python3 fetch-microsoft-terms.py [--target ja-JP|zh-TW|zh-CN|all]

Cache location:
  ~/.cache/translation-toolkit/microsoft-terminology/MicrosoftTermCollection.zip
"""
from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

CACHE_ROOT = Path.home() / ".cache" / "translation-toolkit" / "microsoft-terminology"
SOURCE_URL = "https://download.microsoft.com/download/b/2/d/b2db7a7c-8d33-47f3-b2c1-ee5e6445cf45/MicrosoftTermCollection.zip"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Download Microsoft Terminology Collection to local cache. License: gray; for personal cache only.",
    )
    parser.add_argument(
        "--target",
        choices=["ja-JP", "zh-TW", "zh-CN", "all"],
        default="all",
        help="Target locale (filter applies post-extraction; v0.1 downloads full archive).",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=CACHE_ROOT,
        help=f"Override cache directory (default: {CACHE_ROOT}).",
    )
    args = parser.parse_args(argv)

    args.cache_dir.mkdir(parents=True, exist_ok=True)
    zip_path = args.cache_dir / "MicrosoftTermCollection.zip"

    print(f"Downloading {SOURCE_URL}", file=sys.stderr)
    print(f"  -> {zip_path}", file=sys.stderr)

    try:
        urllib.request.urlretrieve(SOURCE_URL, zip_path)
    except Exception as e:
        print(f"ERROR: download failed: {e}", file=sys.stderr)
        return 1

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"OK: {size_mb:.1f}MB downloaded.", file=sys.stderr)
    print(f"NOTE: Confirm Microsoft Terminology license terms before commercial use.", file=sys.stderr)
    print(f"      Unzip manually or via your tooling — extraction not bundled in v0.1.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
