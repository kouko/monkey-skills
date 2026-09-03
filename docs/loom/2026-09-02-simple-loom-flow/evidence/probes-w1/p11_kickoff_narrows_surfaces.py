#!/usr/bin/env python3
"""P11 — bypass intent.needs-design-recompute by editing the gate's INPUT:
KICKOFF-DEFAULTS `interface-surfaces:` overrides the manifest default, and
the checker reads it with no floor, no ratification and no sign that it was
narrowed. Set it to a glob that matches nothing and `needs-design: no`
becomes unfalsifiable.

TARGET RULE: intent.needs-design-recompute
Attack class: bypass a gate by editing its input.
exit 0 = caught, exit 1 = escaped.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixture import checker, git, new_repo, verdict, write

INTENT = """# add a knob
originator: kouko
kind: engineering
needs-design: no — internal only
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

repo = new_repo("p11")
write(repo, "docs/loom/intent/w1.md", INTENT)
git(repo, "add", "-A")
git(repo, "commit", "-qm", "docs(loom): intent w1\n\nneeds-design: no — internal only")

# Baseline: manifest default surfaces -> the api file must be caught.
write(repo, "src/api/routes.py", "ROUTES = []\n")
git(repo, "add", "-A")
git(repo, "commit", "-qm", "feat: routes")
msg = write(repo, "COMMIT_MSG.txt",
            "docs(loom): intent w1\n\nneeds-design: no — internal only\n")
before = checker(repo, "intent", "docs/loom/intent/w1.md", "--commit-msg", str(msg))

# The attack: narrow the surfaces in the file the gate reads.
write(repo, "docs/loom/KICKOFF-DEFAULTS.md",
      "# Kickoff defaults\n\n- interface-surfaces: docs/nothing/** — "
      "scoped down for this change (2026-09-02)\n")
git(repo, "add", "-A")
git(repo, "commit", "-qm", "chore(loom): kickoff defaults")
after = checker(repo, "intent", "docs/loom/intent/w1.md", "--commit-msg", str(msg))

flipped = before.returncode != 0 and after.returncode == 0
sys.exit(verdict(
    not flipped,
    f"before rc={before.returncode} ({before.stderr.strip()[:120]!r}); "
    f"after narrowing interface-surfaces rc={after.returncode} "
    f"({after.stdout.strip()[:120]!r})",
))
