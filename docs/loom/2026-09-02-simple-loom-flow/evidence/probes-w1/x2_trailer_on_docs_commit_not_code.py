#!/usr/bin/env python3
"""X2 — the `Task: W1-01` trailer is parked on a docs-only commit; the code
commit that actually changed src/thing.py and the attackN.py probes carries
no trailer at all.

check_dispatch_covers_tasks (loom_checker.py:1466) reads the trailer per
COMMIT, not per branch: a trailer on the docs commit does not retroactively
cover the earlier code commit that owes one.

TARGET RULE: push.dispatch-covers-tasks
Attack class: self-exempt via a prose condition (trailer misplacement).
exit 0 = caught, exit 1 = escaped.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixture import (code_repo_with_attacks, git, push_case,
                     review_with_adversarial_commands, verdict, write)

# The code commit carries NO trailer.
repo, _ = code_repo_with_attacks("x2", trailer="")
write(repo, "docs/notes.md", "note\n")
git(repo, "add", "-A")
git(repo, "commit", "-qm", "docs: note\n\nTask: W1-01")

# Make the adversarial probes real passes too, so the trailer question is
# the only thing left for the gate to catch (no masking from a failing
# probe file).
for i in range(3):
    write(repo, f"attack{i}.py", "import sys; sys.exit(0)\n")
git(repo, "add", "-A")
git(repo, "commit", "-qm", "fix: probes exit 0\n\nTask: W1-01")
sha = git(repo, "rev-parse", "HEAD")

rev = review_with_adversarial_commands(sha, [f"python3 attack{i}.py" for i in range(3)])
proc = push_case(repo, rev)

caught = proc.returncode != 0 and "push.dispatch-covers-tasks" in proc.stderr
sys.exit(verdict(
    caught,
    "Task: trailer only on docs/probe commits; the code commit has none; "
    f"rc={proc.returncode}; stderr={proc.stderr.strip()[:300]!r}",
))
