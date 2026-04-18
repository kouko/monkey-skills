# /// script
# requires-python = ">=3.10"
# dependencies = ["finance-datareader>=0.9.90"]
# ///
"""
probe-keystat.py — Enumerate BOK ECOS KEYSTAT codes via FinanceDataReader.

Sweeps K001-K500 (default), recording codes that return non-empty data.
Output:
  - stdout:  Human-readable summary (K-code, first column name, row count, latest date)
  - {out}:   JSON catalog (default: bok-ecos-keystat.json in script dir)

KEYSTAT is BOK's curated ~100대 통계지표 subset. The full ECOS catalog
(thousands of series) requires an API key (free at
https://ecos.bok.or.kr/api/#/AuthKeyApply) — not used here.

Usage:
    uv run probe-keystat.py                    # K001-K500
    uv run probe-keystat.py --start 1 --end 600  # custom range
    uv run probe-keystat.py --out catalog.json   # custom output
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")


def probe(start: int, end: int) -> dict[str, dict]:
    import FinanceDataReader as fdr

    found: dict[str, dict] = {}
    for i in range(start, end + 1):
        code = f"K{i:03d}"
        try:
            df = fdr.DataReader(f"ECOS-KEYSTAT:{code}")
            if df is None or df.empty:
                continue
            cols = list(df.columns)
            found[code] = {
                "rows": len(df),
                "latest": str(df.index[-1])[:10],
                "first_col": cols[0] if cols else None,
                "n_cols": len(cols),
                "start": str(df.index[0])[:10],
            }
            print(
                f"{code}: {cols[0] if cols else '?':40s}  "
                f"{len(df):5d} rows  latest={str(df.index[-1])[:10]}",
                flush=True,
            )
        except Exception:
            pass
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--start", type=int, default=1, help="Start K-code (default 1)")
    parser.add_argument("--end", type=int, default=500, help="End K-code (default 500)")
    parser.add_argument(
        "--out",
        default=str(Path(__file__).parent.parent / "bok-ecos-keystat.json"),
        help="Output JSON path",
    )
    args = parser.parse_args()

    catalog = probe(args.start, args.end)
    Path(args.out).write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
    print(f"\nTotal accessible: {len(catalog)} codes", file=sys.stderr)
    print(f"Saved: {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
