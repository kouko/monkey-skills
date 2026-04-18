#!/usr/bin/env python3
"""
check-scraper-deps.py — report pinned vs PyPI-latest for investing-toolkit
scraper scripts. Powers both the PR-time freshness annotation and the
monthly cron issue.

Scope: parses inline `# /// script` deps in
       investing-toolkit/scripts/*_client.py
       (the "source of truth" scripts; skill-dir copies are ignored to
       avoid double-counting.)

Usage:
  python3 scripts/check-scraper-deps.py                       # human table
  python3 scripts/check-scraper-deps.py --format markdown     # GitHub-ready
  python3 scripts/check-scraper-deps.py --fail-on major       # exit 1 if
                                                              # major drift

Exit codes:
  0 — report OK (or all in-sync, depending on --fail-on)
  1 — drift exceeds threshold
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "investing-toolkit" / "scripts"

# Libraries we actively care about (the "scraper surface" that rots fast).
# Everything pinned that isn't on this list is still reported but without
# the "scraper" tag.
SCRAPER_LIBS = {
    "yfinance",
    "akshare",
    "finance-datareader",
    "finmind",
    "curl_cffi",
    "beautifulsoup4",
    "lxml",
}

# `# dependencies = ["pkg==1.2.3", "other>=0.4", ...]`
DEPS_LINE_RE = re.compile(r"#\s*dependencies\s*=\s*\[(.*?)\]", re.DOTALL)
PINNED_RE = re.compile(r'"([A-Za-z0-9_.\-]+)\s*==\s*([0-9][^"]*)"')


def parse_deps(py_file: Path) -> list[tuple[str, str]]:
    """Extract exactly-pinned (== version) deps from a uv-style inline
    script header. Returns [(pkg, pinned_version), ...]."""
    text = py_file.read_text(encoding="utf-8", errors="replace")
    m = DEPS_LINE_RE.search(text)
    if not m:
        return []
    return [(pkg, ver) for pkg, ver in PINNED_RE.findall(m.group(1))]


def fetch_pypi_latest(pkg: str) -> str | None:
    """Fetch latest stable version from PyPI JSON API. Returns None on
    error so the caller can show '?' instead of failing the whole run."""
    url = f"https://pypi.org/pypi/{pkg}/json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "monkey-skills/ci"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
        return data.get("info", {}).get("version")
    except Exception:
        return None


def _version_tuple(v: str) -> tuple[int, ...]:
    """Coerce 'X.Y.Z' / 'X.Y' / 'X.Y.Za1' into a comparable tuple of
    leading numeric components. Non-numeric tails are treated as 0 for
    the purposes of rough drift detection."""
    parts: list[int] = []
    for chunk in v.split("."):
        m = re.match(r"(\d+)", chunk)
        if not m:
            break
        parts.append(int(m.group(1)))
    return tuple(parts) or (0,)


def classify_drift(pinned: str, latest: str | None) -> str:
    """Return one of: 'synced', 'patch', 'minor', 'major', 'unknown'."""
    if latest is None:
        return "unknown"
    if pinned == latest:
        return "synced"
    p = _version_tuple(pinned)
    l = _version_tuple(latest)
    # Pad to same length
    while len(p) < len(l):
        p = p + (0,)
    while len(l) < len(p):
        l = l + (0,)
    if l[0] > p[0]:
        return "major"
    if len(l) > 1 and l[1] > p[1]:
        return "minor"
    return "patch"


DRIFT_ORDER = {"synced": 0, "patch": 1, "minor": 2, "major": 3, "unknown": 4}
FAIL_THRESHOLDS = {"patch": 1, "minor": 2, "major": 3}  # via --fail-on


def collect_reports() -> list[dict]:
    """Walk *_client.py files, collect unique (pkg, pinned) pairs, query
    PyPI once per package, return sorted records."""
    client_files = sorted(SCRIPTS_DIR.glob("*_client.py"))
    seen: dict[tuple[str, str], list[str]] = {}
    for py in client_files:
        for pkg, ver in parse_deps(py):
            key = (pkg, ver)
            seen.setdefault(key, []).append(py.name)

    records = []
    for (pkg, pinned), files in sorted(seen.items()):
        latest = fetch_pypi_latest(pkg)
        drift = classify_drift(pinned, latest)
        records.append(
            {
                "pkg": pkg,
                "pinned": pinned,
                "latest": latest or "?",
                "drift": drift,
                "files": files,
                "scraper": pkg.lower() in SCRAPER_LIBS,
            }
        )
    return records


def _emoji(drift: str) -> str:
    return {
        "synced": "✅",
        "patch": "🟢",
        "minor": "🟡",
        "major": "🔴",
        "unknown": "❔",
    }.get(drift, "?")


def render_text(records: list[dict]) -> str:
    lines = []
    lines.append(f"{'pkg':<22} {'pinned':<10} {'latest':<10} {'drift':<8} scraper")
    lines.append("-" * 66)
    for r in records:
        tag = "S" if r["scraper"] else " "
        lines.append(
            f"{r['pkg']:<22} {r['pinned']:<10} {r['latest']:<10} "
            f"{_emoji(r['drift'])} {r['drift']:<6} {tag}"
        )
    return "\n".join(lines)


def render_markdown(records: list[dict]) -> str:
    header = (
        "# investing-toolkit scraper dependency report\n\n"
        "Scripts scanned: `investing-toolkit/scripts/*_client.py`. "
        "Pinned = current `==X.Y.Z` in inline `uv` script header. "
        "Latest = PyPI stable release.\n\n"
        "| Package | Pinned | Latest | Drift | Scraper | Used by |\n"
        "|---|---|---|---|---|---|\n"
    )
    rows = []
    for r in records:
        scraper_tag = "yes" if r["scraper"] else ""
        files = ", ".join(f"`{f}`" for f in r["files"])
        rows.append(
            f"| `{r['pkg']}` | `{r['pinned']}` | `{r['latest']}` | "
            f"{_emoji(r['drift'])} {r['drift']} | {scraper_tag} | {files} |"
        )
    legend = (
        "\n\n**Legend** — ✅ synced · 🟢 patch behind · 🟡 minor behind · "
        "🔴 major behind · ❔ PyPI lookup failed. "
        "Scraper-tagged libs (yfinance, akshare, finance-datareader, finmind, "
        "curl_cffi, beautifulsoup4, lxml) rot fastest against upstream "
        "anti-bot changes; prioritise upgrading those.\n"
    )
    return header + "\n".join(rows) + legend


def should_fail(records: list[dict], threshold: str | None) -> bool:
    if not threshold:
        return False
    limit = FAIL_THRESHOLDS.get(threshold)
    if limit is None:
        return False
    return any(DRIFT_ORDER.get(r["drift"], 0) >= limit for r in records)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--format",
        choices=("text", "markdown"),
        default="text",
        help="Output format (default: text)",
    )
    ap.add_argument(
        "--fail-on",
        choices=("patch", "minor", "major"),
        default=None,
        help="Exit 1 if any dep has this drift or worse (default: never fail)",
    )
    ap.add_argument(
        "--scrapers-only",
        action="store_true",
        help="Only report packages in the scraper allowlist",
    )
    args = ap.parse_args()

    if not SCRIPTS_DIR.is_dir():
        print(f"error: {SCRIPTS_DIR} not found", file=sys.stderr)
        return 2

    records = collect_reports()
    if args.scrapers_only:
        records = [r for r in records if r["scraper"]]

    out = render_markdown(records) if args.format == "markdown" else render_text(records)
    print(out)

    return 1 if should_fail(records, args.fail_on) else 0


if __name__ == "__main__":
    sys.exit(main())
