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

Optional layer-2 deny-list (OFF by default, never blocks when absent — the
scanner stays zero-config): a plain-text file, one literal term per line
(blank lines and `#`-comment lines ignored), for catching a user's own
sensitive literals (company names, project codenames) that the generic
secrets patterns above can't know about. Resolution order:
  1. --denylist <path>
  2. GIT_MEMORY_DENYLIST env var (a path)
  3. none — scans secrets-only, notes "denylist: not configured" on stderr
A --denylist/env path that doesn't exist also fails OPEN (secrets-only,
stderr notes the file was not found) — this optional layer never blocks.
A deny-list file that exists but is unreadable/undecodable (e.g. invalid
UTF-8) also fails OPEN: a clean stderr note, secrets-only scanning
continues. Matching is case-insensitive. Deny-list findings are redacted
with a fixed "[redacted]" marker (never a term prefix — deny-list terms
have no length guarantee, unlike secrets).

Usage:
  privacy-scan.py --text-file <path> [--denylist <path>]
  <producer> | privacy-scan.py           # stdin when no --text-file given

Output: a JSON list of findings to stdout — [] when clean.
Each finding: {"pattern": <name>, "line": <1-indexed line number>,
               "match_redacted": <first few chars + "…">}

Exit codes:
  0  clean (no findings)
  1  bad --text-file input
  3  one or more findings
"""

from __future__ import annotations

import argparse
import json
import os
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


# Deny-list terms have no length guarantee (company/person names can be as
# short as 3-4 chars — "IBM", "Visa", "3M"), so the secrets-layer prefix
# redaction above (first 4 chars + "…") would reveal such a term IN FULL.
# Deny-list findings use a fixed marker that echoes zero characters of the
# term instead; the line number still lets the user locate the match.
DENYLIST_REDACTED_MARKER = "[redacted]"


def load_denylist_terms(path: Path) -> list[str]:
    """Read one literal term per line; blank lines and `#`-comments ignored."""
    terms: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        terms.append(line)
    return terms


def resolve_denylist_path(cli_path: Path | None) -> Path | None:
    """--denylist flag wins over GIT_MEMORY_DENYLIST env; neither -> None."""
    if cli_path is not None:
        return cli_path
    env_path = os.environ.get("GIT_MEMORY_DENYLIST")
    return Path(env_path) if env_path else None


def scan_text(text: str, denylist_terms: list[str] | None = None) -> list[dict]:
    """Scan text line-by-line against PATTERNS (and optional deny-list terms);
    return a list of findings."""
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
        for term in denylist_terms or []:
            if term.lower() in line.lower():
                findings.append(
                    {
                        "pattern": "denylist",
                        "line": lineno,
                        "match_redacted": DENYLIST_REDACTED_MARKER,
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
    parser.add_argument(
        "--denylist",
        type=Path,
        default=None,
        help=(
            "Optional path to a deny-list file (one literal term per line, "
            "'#'-comments and blank lines ignored). Falls back to "
            "GIT_MEMORY_DENYLIST env var; absent entirely -> secrets-only "
            "scan (fail-open, never blocks)."
        ),
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

    denylist_path = resolve_denylist_path(args.denylist)
    denylist_terms: list[str] = []
    if denylist_path is None:
        print("denylist: not configured", file=sys.stderr)
    elif not denylist_path.exists():
        print(f"denylist: file not found: {denylist_path}", file=sys.stderr)
    else:
        try:
            denylist_terms = load_denylist_terms(denylist_path)
        except (OSError, UnicodeDecodeError) as exc:
            print(f"denylist: cannot read file, skipping: {exc}", file=sys.stderr)

    findings = scan_text(text, denylist_terms)
    json.dump(findings, sys.stdout)
    sys.stdout.write("\n")
    return 3 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
