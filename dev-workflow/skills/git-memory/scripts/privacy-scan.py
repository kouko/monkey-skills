#!/usr/bin/env python3
"""privacy-scan.py — layer-1 deterministic secrets scan for the close-out privacy gate.

Scans composed commit/PR TEXT (not code diffs) for hardcoded secrets, so that
when the human approval step is removed from close-out, leaked credentials are
still caught before push. Zero configuration — works in any repo with no setup.

Pattern set (core gitleaks-style classes — see
loom-code/skills/subagent-driven-development/checklists/security-checklist.md
CHK-SEC-001):
  - AWS access key            AKIA[0-9A-Z]{16}
  - GitHub token               ghp_/gho_ + alnum
  - Slack token / webhook      xox[baprs]-... / hooks.slack.com/services/...
  - PEM private-key header     -----BEGIN ... PRIVATE KEY-----
  - Generic secret assignment  (API_?KEY|TOKEN|SECRET|PASSWORD) [=:] <>=16 chars>

Usage:
  privacy-scan.py --text-file <path>
  <producer> | privacy-scan.py           # stdin when no --text-file given

Output: a JSON list of findings to stdout — [] when clean.
Each finding: {"pattern": <name>, "line": <1-indexed line number>,
               "match_redacted": <first few chars + "…">}

Exit codes:
  0  clean (no findings)
  3  one or more findings
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# LOOM-SIMPLIFY: generic_secret_assignment flags any >=16-char non-space
# token after KEY/TOKEN/SECRET/PASSWORD by length alone — no real
# Shannon-entropy scoring | ceiling: if this pattern's false-positive rate
# becomes a recorded friction point in docs/loom/memory/ after real
# close-out usage | upgrade: replace the length check with a
# Shannon-entropy threshold (bits/char) on the captured value | ref:
# docs/loom/plans/2026-07-19-closeout-privacy-gate.md Task 1
PATTERNS: list[tuple[str, "re.Pattern[str]", int]] = [
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}"), 0),
    (
        "github_token",
        re.compile(
            r"(?:gh[po]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9]{22}_[A-Za-z0-9]{59})"
        ),
        0,
    ),
    ("slack_token", re.compile(r"xox[baprs]-[A-Za-z0-9-]+"), 0),
    (
        "slack_webhook",
        re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9/]+"),
        0,
    ),
    (
        "pem_private_key",
        re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
        0,
    ),
    (
        "generic_secret_assignment",
        re.compile(
            r"(?i)(?:API_?KEY|TOKEN|SECRET|PASSWORD)\s*[=:]\s*['\"]?([^\s'\"]{16,})"
        ),
        1,
    ),
]


def redact(secret: str) -> str:
    """Show only the first few characters of a matched secret, never the full value."""
    prefix = secret[:4]
    return f"{prefix}…"


def scan_text(text: str) -> list[dict]:
    """Scan text line-by-line against PATTERNS; return a list of findings."""
    findings: list[dict] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for name, regex, group in PATTERNS:
            for match in regex.finditer(line):
                secret = match.group(group)
                findings.append(
                    {
                        "pattern": name,
                        "line": lineno,
                        "match_redacted": redact(secret),
                    }
                )
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--text-file",
        type=Path,
        default=None,
        help="Path to the composed text to scan. Reads stdin if omitted.",
    )
    args = parser.parse_args(argv)

    if args.text_file is not None:
        try:
            text = args.text_file.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"privacy-scan.py: cannot read --text-file: {exc}", file=sys.stderr)
            return 1
    else:
        text = sys.stdin.read()

    findings = scan_text(text)
    json.dump(findings, sys.stdout)
    sys.stdout.write("\n")
    return 3 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
