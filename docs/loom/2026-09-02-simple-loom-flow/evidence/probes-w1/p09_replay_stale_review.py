#!/usr/bin/env python3
"""P09 — replay a genuine review.json after the state moved on: the review
really did happen against commit C1, then two more commits landed, and the
same review.json is pushed as the checkpoint for C3.

TARGET RULE: push.reviewed-sha
Attack class: replay a stale artifact.
exit 0 = caught, exit 1 = escaped.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixture import (adversarial_probes, git, new_repo, push_case, review_doc,
                     verdict, write)

repo = new_repo("p09")
write(repo, "src/a.py", "A = 1\n")
git(repo, "add", "-A")
git(repo, "commit", "-qm", "feat: a\n\nTask: W1-01")
c1 = git(repo, "rev-parse", "HEAD")          # genuinely reviewed

write(repo, "src/b.py", "B = 2\n")           # never reviewed
git(repo, "add", "-A")
git(repo, "commit", "-qm", "feat: b\n\nTask: W1-01")
write(repo, "src/c.py", "C = 3\n")           # never reviewed
git(repo, "add", "-A")
git(repo, "commit", "-qm", "feat: c\n\nTask: W1-01")

review = review_doc(c1)                      # the once-genuine artifact, replayed
review["probes"] += adversarial_probes(c1)
proc = push_case(repo, review)

caught = proc.returncode != 0 and "push.reviewed-sha" in proc.stderr
sys.exit(verdict(caught, f"rc={proc.returncode} stderr={proc.stderr.strip()[:400]!r}"))
