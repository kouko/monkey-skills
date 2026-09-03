#!/usr/bin/env python3
"""P03 — a "review-only" commit that also DELETES a second file, hidden by
rename detection.

push.review-only-head reads `git show --name-only` and demands exactly one
path. Rename detection collapses a delete+add pair into a single line, so a
HEAD commit that renames a tracked source file INTO the review.json path
removes that source file from the tree while the gate sees one path.

TARGET RULE: push.review-only-head
Attack class: bypass a gate by editing its input.
exit 0 = caught, exit 1 = escaped.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixture import (adversarial_probes, checker, git, new_repo, review_doc,
                     verdict, write)

repo = new_repo("p03")
write(repo, "src/thing.py", "def f():\n    return 1\n")
git(repo, "add", "-A")
git(repo, "commit", "-qm", "feat: thing\n\nTask: W1-01")

# The implementation commit legitimately adds a source file whose bytes are
# (by the attacker's choice) already almost the review body.
decoy = review_doc("0" * 40)
decoy["probes"] += adversarial_probes("0" * 40)
write(repo, "src/generated_fixture.json", json.dumps(decoy, indent=2) + "\n")
git(repo, "add", "-A")
git(repo, "commit", "-qm", "feat: fixture\n\nTask: W1-01")
sha = git(repo, "rev-parse", "HEAD")

(repo / "docs" / "loom" / "w1").mkdir(parents=True, exist_ok=True)
# HEAD: rename the source file away and patch the shas in the same commit.
# Similarity stays ~99%, so git reports one renamed path, not add+delete.
git(repo, "mv", "src/generated_fixture.json", "docs/loom/w1/review.json")
real = review_doc(sha)
real["probes"] += adversarial_probes(sha)
write(repo, "docs/loom/w1/review.json", json.dumps(real, indent=2) + "\n")
git(repo, "add", "-A")
git(repo, "commit", "-qm", "chore(loom): review checkpoint")

listing = [ln for ln in git(repo, "show", "--name-only", "--pretty=format:", "HEAD").splitlines() if ln.strip()]
gone = not (repo / "src" / "generated_fixture.json").exists()
proc = checker(repo, "push")

caught = "review-only-head" in proc.stderr
sys.exit(verdict(
    caught,
    f"rc={proc.returncode}; --name-only printed {listing!r}; "
    f"src/generated_fixture.json deleted by the same commit={gone}; "
    f"stderr={proc.stderr.strip()[:400]!r}",
))
