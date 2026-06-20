#!/usr/bin/env python3
"""check-shared-conventions-drift.py — verify shared convention files stay in sync.

Cross-skill regression CI: when the same convention is bundled in
multiple skills as functional copies (per the SSOT-and-functional-
copy pattern from PR #159 / dev-workflow PR-2/PR-3), edits must land
in **all** copies in the same PR. This script enforces that rule by
diffing the body content (everything after the header blockquote)
of each shared convention across all skills that bundle it.

Currently checks:

  skill-dev-toolkit/skills/skill-refactor/references/golden-anchor-protocol.md
  vs
  skill-dev-toolkit/skills/skill-tuning/references/golden-anchor-protocol.md

  skill-dev-toolkit/skills/skill-refactor/references/test-prompts-schema.md
  vs
  skill-dev-toolkit/skills/skill-tuning/references/test-prompts-schema.md

  skill-dev-toolkit/skills/skill-refactor/references/constitution-schema.md
  vs
  skill-dev-toolkit/skills/skill-tuning/references/constitution-schema.md

The header blockquote (lines starting with `>` immediately after
the H1 heading) is intentionally **different** between SSOT location
and functional copies (SSOT marks itself as canonical; copies point
back). We strip the header blockquote before diffing so legitimate
header divergence doesn't trigger false positives.

Usage:
    python3 scripts/check-shared-conventions-drift.py

Exit codes:
    0 — all shared convention files in sync
    1 — drift detected (body content differs between copies)
    2 — file missing or unreadable

Future extension: add per-plugin convention manifests so this script
can scale beyond hand-coded pairs.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Convention pair manifest
# ---------------------------------------------------------------------------


class ConventionPair(NamedTuple):
    name: str
    canonical_path: Path  # The SSOT location
    functional_copies: list[Path]  # Paths that should mirror canonical body


SHARED_CONVENTIONS: list[ConventionPair] = [
    ConventionPair(
        name="golden-anchor-protocol",
        canonical_path=REPO_ROOT
        / "skill-dev-toolkit/skills/skill-refactor/references/golden-anchor-protocol.md",
        functional_copies=[
            REPO_ROOT
            / "skill-dev-toolkit/skills/skill-tuning/references/golden-anchor-protocol.md",
        ],
    ),
    ConventionPair(
        name="test-prompts-schema",
        canonical_path=REPO_ROOT
        / "skill-dev-toolkit/skills/skill-refactor/references/test-prompts-schema.md",
        functional_copies=[
            REPO_ROOT
            / "skill-dev-toolkit/skills/skill-tuning/references/test-prompts-schema.md",
        ],
    ),
    ConventionPair(
        name="constitution-schema",
        canonical_path=REPO_ROOT
        / "skill-dev-toolkit/skills/skill-refactor/references/constitution-schema.md",
        functional_copies=[
            REPO_ROOT
            / "skill-dev-toolkit/skills/skill-tuning/references/constitution-schema.md",
        ],
    ),
]


# ---------------------------------------------------------------------------
# Header-blockquote stripping
# ---------------------------------------------------------------------------

# After the H1 heading, an optional blockquote block (lines starting with `>`)
# describes the SSOT-vs-copy relationship. This block is intentionally
# different between canonical and functional copies, so we strip it before
# diffing. Pattern: H1 line → blank line → blockquote lines (each starting
# with `>` or `> `) → blank line → body.

H1_RE = re.compile(r"^# .+$", re.MULTILINE)


def strip_header_blockquote(text: str) -> str:
    """Remove the header blockquote that follows the H1, leaving the body.

    Returns text with H1 line preserved but the immediately-following
    blockquote (and surrounding blank lines) removed.
    """
    lines = text.splitlines(keepends=False)
    if not lines:
        return text

    # Find the first H1 line.
    h1_idx = None
    for i, line in enumerate(lines):
        if line.startswith("# "):
            h1_idx = i
            break
    if h1_idx is None:
        return text  # No H1; return as-is.

    # Walk forward from H1 over blank lines and blockquote lines, dropping them.
    keep_lines = lines[: h1_idx + 1]
    i = h1_idx + 1
    in_blockquote_section = False

    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        if stripped.startswith("> ") or stripped == ">":
            # In or entering blockquote section.
            in_blockquote_section = True
            i += 1
            continue
        if line.strip() == "":
            # Blank line inside / around blockquote — skip.
            if in_blockquote_section:
                i += 1
                continue
            # Pre-blockquote blank lines are also skipped to avoid drift over
            # whitespace.
            i += 1
            continue
        # Non-blank, non-blockquote → start of body.
        if in_blockquote_section:
            keep_lines.append("")  # one blank separator before body
        break

    keep_lines.extend(lines[i:])
    return "\n".join(keep_lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Diff
# ---------------------------------------------------------------------------


def read_or_error(path: Path) -> str | None:
    if not path.exists():
        print(f"  ERROR: file does not exist: {path}", file=sys.stderr)
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as e:
        print(f"  ERROR: cannot read {path}: {e}", file=sys.stderr)
        return None


def check_pair(pair: ConventionPair) -> tuple[int, int]:
    """Return (failures, errors) for this convention pair."""
    print(f"\nConvention: {pair.name}")
    print(f"  Canonical: {pair.canonical_path.relative_to(REPO_ROOT)}")

    canonical_text = read_or_error(pair.canonical_path)
    if canonical_text is None:
        return 0, 1

    canonical_body = strip_header_blockquote(canonical_text)
    failures = 0
    errors = 0

    for copy_path in pair.functional_copies:
        rel = copy_path.relative_to(REPO_ROOT)
        copy_text = read_or_error(copy_path)
        if copy_text is None:
            errors += 1
            continue

        copy_body = strip_header_blockquote(copy_text)

        if canonical_body == copy_body:
            print(f"  PASS  {rel}")
        else:
            print(f"  FAIL  {rel}")
            print(
                "    Bodies differ. Edit the canonical first, then mirror to "
                "this copy in the same PR. The header blockquote is "
                "intentionally different between SSOT and functional copies "
                "and is stripped before this diff."
            )
            # Emit a small diff hint
            canonical_lines = canonical_body.splitlines()
            copy_lines = copy_body.splitlines()
            diff_count = 0
            for cl, kl in zip(canonical_lines, copy_lines):
                if cl != kl and diff_count < 3:
                    print(f"    canonical: {cl[:80]!r}")
                    print(f"    copy     : {kl[:80]!r}")
                    diff_count += 1
            if len(canonical_lines) != len(copy_lines):
                print(
                    f"    line counts differ: canonical={len(canonical_lines)}, "
                    f"copy={len(copy_lines)}"
                )
            failures += 1

    return failures, errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    print("check-shared-conventions-drift: verifying SSOT-and-functional-copy sync\n")

    total_failures = 0
    total_errors = 0
    for pair in SHARED_CONVENTIONS:
        failures, errors = check_pair(pair)
        total_failures += failures
        total_errors += errors

    print(
        f"\n{len(SHARED_CONVENTIONS)} convention(s) checked, "
        f"{total_failures} drift failure(s), {total_errors} read error(s)"
    )

    if total_errors:
        return 2
    if total_failures:
        return 1
    print("All shared conventions in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
