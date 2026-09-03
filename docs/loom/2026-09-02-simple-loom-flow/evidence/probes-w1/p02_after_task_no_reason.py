#!/usr/bin/env python3
"""P02 — a plan.md with THREE `review: after-task` tasks and no reason line
on the third (write-plan/SKILL.md:353 budgets 2 per plan; each extra one
"carries a one-line reason on that task"). Is anything mechanical checking
that budget or that reason?

TARGET RULE: none exists — the probe's verdict is whether one should. This
plan.md does not touch a `code`/`spec`/`skill`/`gate` artifact type, so
push.dispatch-covers-tasks stays silent and cannot mask the result; the
grep over the enforcing surfaces is the actual measurement here.
Attack class: self-exempt via a prose condition.
exit 0 = caught, exit 1 = escaped.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixture import (REPO_UNDER_AUDIT, adversarial_probes, checker, git,
                     new_repo, push_case, review_doc, verdict, write)

PLAN = """# Plan — w1

## Current State Evidence
- Forward: src/thing.py:1
- Reverse: src/thing.py:1
- Error: src/thing.py:1
- Data: src/thing.py:1
- Boundary: src/thing.py:1

## Task DAG
**W1-01 first** after: none review: after-task
**W1-02 second** after: W1-01 review: after-task
**W1-03 third** after: W1-02 review: after-task
**W1-04 fourth** after: W1-03 review: after-task

## Risks
- none
"""

repo = new_repo("p02")
write(repo, "docs/loom/w1/plan.md", PLAN)
git(repo, "add", "docs/loom/w1/plan.md")
git(repo, "commit", "-qm", "docs(loom): plan")
sha = git(repo, "rev-parse", "HEAD")

review = review_doc(sha)
review["probes"] += adversarial_probes(sha)
proc = push_case(repo, review)

# Does any checker rule even mention the after-task budget?
rules = checker(repo, "--list-rules").stdout
# Only ENFORCING surfaces count: the checker, check_mechanisms.py, hooks.json.
# Test files and manifest prose merely repeat the rule; they enforce nothing.
enforcers = [REPO_UNDER_AUDIT / "loom-code" / "scripts" / "loom_checker.py",
             REPO_UNDER_AUDIT / "loom-code" / "scripts" / "check_mechanisms.py",
             REPO_UNDER_AUDIT / "loom-code" / "hooks" / "hooks.json"]
grep = subprocess.run(["grep", "-In", "after-task", *map(str, enforcers)],
                      capture_output=True, text=True)
mechanical = bool(grep.stdout.strip()) or "after-task" in rules

caught = proc.returncode != 0 or mechanical
sys.exit(verdict(
    caught,
    f"push rc={proc.returncode}; no checker rule names after-task "
    f"(grep over loom_checker/check_mechanisms/hooks.json hits={len(grep.stdout.splitlines())}); "
    f"stderr={proc.stderr.strip()[:200]!r}",
))
