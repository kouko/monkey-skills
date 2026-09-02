#!/usr/bin/env python3
"""P13 — race two concurrent writers on review.json.

build/SKILL.md:139 says every dispatch appends an entry to
docs/loom/<change-id>/review.json. Two implementers dispatched in parallel
(build/SKILL.md:66 explicitly dispatches them in one message) each
read-modify-write that same file. Nothing locks it.

The probe interleaves two read-modify-write cycles the way parallel agents
do, then asks the push gate whether the lost entry is visible.

TARGET RULE: push.dispatch-covers-tasks (catches the lost writer as a
missing implementer entry for a trailered task, not as a race per se).
Attack class: race a concurrent writer.
exit 0 = caught, exit 1 = escaped.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixture import (adversarial_probes, git, new_repo, push_case, review_doc,
                     verdict, write)

repo = new_repo("p13")
write(repo, "src/a.py", "A = 1\n")
write(repo, "src/b.py", "B = 2\n")
git(repo, "add", "-A")
# Two trailers: this fixture stands in for two tasks (W1-01, W1-02) whose
# implementer dispatch entries race below -- without both trailers the
# missing-trailer branch of dispatch-covers-tasks would fire regardless of
# the race, masking the thing this probe actually measures.
git(repo, "commit", "-qm", "feat: a+b\n\nTask: W1-01\nTask: W1-02")
sha = git(repo, "rev-parse", "HEAD")

base = review_doc(sha)
base["probes"] += adversarial_probes(sha)
base["dispatch"] = [e for e in base["dispatch"] if e["role"] != "implementer"]
path = write(repo, "docs/loom/w1/review.json", json.dumps(base, indent=2) + "\n")

# Both agents READ the same bytes...
snap_a = json.loads(path.read_text())
snap_b = json.loads(path.read_text())
# ...each appends its own dispatch entry...
snap_a["dispatch"].append({"task": "W1-01", "role": "implementer", "agent_id": "imp-a",
                           "model": "m", "started": "2026-09-02T00:00:01Z",
                           "fresh_context": True})
snap_b["dispatch"].append({"task": "W1-02", "role": "implementer", "agent_id": "imp-b",
                           "model": "m", "started": "2026-09-02T00:00:02Z",
                           "fresh_context": True})
# ...and writes. B lands last; A's entry is gone.
path.write_text(json.dumps(snap_a, indent=2) + "\n", encoding="utf-8")
path.write_text(json.dumps(snap_b, indent=2) + "\n", encoding="utf-8")

final = json.loads(path.read_text())
ids = [e["agent_id"] for e in final["dispatch"]]
lost = "imp-a" not in ids

git(repo, "add", "-A")
git(repo, "commit", "-qm", "chore(loom): review checkpoint")
from fixture import checker  # noqa: E402
proc = checker(repo, "push")

# The gate catches the race only if it refuses a record that lost a writer.
caught = (not lost) or (
    proc.returncode != 0 and "push.dispatch-covers-tasks" in proc.stderr
)
sys.exit(verdict(
    caught,
    f"dispatch[] after the interleave={ids!r} (imp-a lost={lost}); "
    f"push rc={proc.returncode} stderr={proc.stderr.strip()[:250]!r}",
))
