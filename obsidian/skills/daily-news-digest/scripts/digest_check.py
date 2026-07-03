#!/usr/bin/env python3
"""digest_check.py — consolidated digest self-check gate (STEP 7).

One command, one verdict, exit code decides:

    python3 digest_check.py <vault_root> <digest_path> [--skip-mermaid]

Checks (all must pass → exit 0, "ALL PASS"):
  1. COT completeness — every `### ` story heading in the news section
     (before the knowledge tier) has a `flowchart LR` diagram: LR count
     ≥ story count.
  2. Link resolution — every [[wikilink]] stem resolves to a real .md
     file under the vault root (page-anchor-only links are exempt).
  3. Mermaid syntax — every block parses via scripts/validate.sh
     (mermaid-cli through npx). --skip-mermaid skips this check ONLY
     for offline unit tests; never pass it in a real digest run.

Any FAIL prints the offending items and exits 1 — fix the digest and
re-run until exit 0. This gate is a repair loop, not a report.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("vault_root")
    ap.add_argument("digest_path")
    ap.add_argument("--skip-mermaid", action="store_true",
                    help="unit tests only — never use in a real run")
    args = ap.parse_args()

    root = Path(args.vault_root)
    digest = Path(args.digest_path)
    doc = digest.read_text(encoding="utf-8")
    failures: list[str] = []

    # 1. COT completeness — both counts scoped to the news section, so a
    # knowledge-tier CoT can't mask a story missing its diagram
    news = doc.split("## 🧠")[0] if "## 🧠" in doc else doc
    stories = len(re.findall(r"^### ", news, re.M))
    cots = len(re.findall(r"^flowchart LR", news, re.M))
    if cots < stories:
        failures.append(f"cot: {stories - cots} story/stories missing a flowchart LR "
                        f"({stories} stories vs {cots} LR diagrams) — add before finishing")
    print(f"[1 cot] stories={stories} LR-diagrams={cots}")

    # 2. Link resolution
    links = {m.split("|")[0].split("#")[0].strip()
             for m in re.findall(r"\[\[([^\]]+)\]\]", doc)}
    stems = set()
    for dirpath, dirnames, files in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        stems.update(f[:-3] for f in files if f.endswith(".md"))
    broken = sorted(links - stems - {""})  # "" = page-anchor-only links, not broken
    if broken:
        failures.append(f"links: broken wikilink targets {broken}")
    print(f"[2 links] broken={broken or 'none'}")

    # 3. Mermaid syntax via validate.sh
    if args.skip_mermaid:
        print("[3 mermaid] SKIPPED (--skip-mermaid: unit tests only)")
    else:
        validate = Path(__file__).parent / "validate.sh"
        r = subprocess.run(["bash", str(validate), str(digest)],
                           capture_output=True, text=True, cwd=root)
        out = r.stdout + r.stderr
        fails = re.findall(r"^FAIL.*$", out, re.M)
        passes = len(re.findall(r"^PASS", out, re.M))
        if fails or r.returncode != 0:
            failures.append(f"mermaid: {fails or 'validate.sh exited non-zero'}")
        print(f"[3 mermaid] pass={passes} fail={fails or 'none'}")

    if failures:
        print("\nRESULT: FAIL — fix these in THIS run, then re-run digest_check until ALL PASS:")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print("\nRESULT: ALL PASS ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
