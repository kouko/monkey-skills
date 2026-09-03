#!/usr/bin/env python3
"""P05 — `needs-design: no` was honest at intake, but the change later grew
an interface-surface file that is still UNTRACKED (never `git add`ed).

intent.needs-design-recompute recomputes from changed_paths(); the question
is whether that set includes `ls-files --others`.

TARGET RULE: intent.needs-design-recompute
Attack class: replay a stale artifact (an intake-time claim reused after the
state moved on).
exit 0 = caught, exit 1 = escaped.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixture import checker, git, new_repo, verdict, write

INTENT = """# add a knob
originator: kouko
kind: engineering
needs-design: no — internal only, no interface change
status: confirmed 2026-09-02

## Problem
The retry delay is fixed.

## Proposed outcome
Make it configurable.

## Acceptance
1. The delay can be set.

## Constraints
- none

## Out of scope
- none

## Open questions
- none
"""

repo = new_repo("p05")
write(repo, "docs/loom/intent/w1.md", INTENT)
git(repo, "add", "-A")
git(repo, "commit", "-qm",
    "docs(loom): intent w1\n\nneeds-design: no — internal only, no interface change")

# The interface file exists on disk but was never staged.
write(repo, "src/api/routes.py", "ROUTES = []\n")

proc = checker(repo, "intent", "docs/loom/intent/w1.md")
caught = proc.returncode != 0 and "needs-design-recompute" in proc.stderr
sys.exit(verdict(
    caught,
    f"rc={proc.returncode} stdout={proc.stdout.strip()[:200]!r} "
    f"stderr={proc.stderr.strip()[:300]!r}",
))
