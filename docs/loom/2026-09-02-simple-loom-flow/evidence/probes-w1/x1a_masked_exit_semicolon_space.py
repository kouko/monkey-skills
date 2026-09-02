#!/usr/bin/env python3
"""X1a — reviewer-authored probe: the recorded adversarial command is
`python3 attackN.py ; true` (space before the semicolon). attackN.py really
exits 1 (a genuine adversarial failure), but the trailing `; true` masks
the shell's exit code the checker re-runs the command with.

TARGET RULE: push.probes-adversarial
Attack class: forge an artifact the gate trusts (command-level masking).
exit 0 = caught, exit 1 = escaped.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixture import (code_repo_with_attacks, push_case,
                     review_with_adversarial_commands, verdict)

repo, sha = code_repo_with_attacks("x1a")
rev = review_with_adversarial_commands(sha, [f"python3 attack{i}.py ; true" for i in range(3)])
proc = push_case(repo, rev)

caught = proc.returncode != 0 and "push.probes-adversarial" in proc.stderr
sys.exit(verdict(
    caught,
    "adversarial cmd `python3 attackN.py ; true` (attackN exits 1, masked by "
    f"`; true`); rc={proc.returncode}; stderr={proc.stderr.strip()[:300]!r}",
))
