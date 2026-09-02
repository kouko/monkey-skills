#!/usr/bin/env python3
"""X1c — control for X1a/X1b: the bare command `python3 attackN.py`
(really exits 1, no masking suffix) must block. Without this control, a
"caught" result on X1a/X1b would not prove the masking suffix is what
mattered.

TARGET RULE: push.probes-adversarial
Attack class: control (no attack) -- an honest failing probe.
exit 0 = caught, exit 1 = escaped.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixture import (code_repo_with_attacks, push_case,
                     review_with_adversarial_commands, verdict)

repo, sha = code_repo_with_attacks("x1c")
rev = review_with_adversarial_commands(sha, [f"python3 attack{i}.py" for i in range(3)])
proc = push_case(repo, rev)

caught = proc.returncode != 0 and "push.probes-adversarial" in proc.stderr
sys.exit(verdict(
    caught,
    f"control: bare `python3 attackN.py` (exits 1) must block; "
    f"rc={proc.returncode}; stderr={proc.stderr.strip()[:200]!r}",
))
