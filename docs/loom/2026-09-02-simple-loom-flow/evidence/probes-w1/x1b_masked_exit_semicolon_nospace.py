#!/usr/bin/env python3
"""X1b — same attack as X1a, but no space before the semicolon: the
recorded command is `python3 attackN.py; true`, so the shlex token
immediately preceding the separator is `attackN.py;` rather than
`attackN.py`.

TARGET RULE: push.probes-adversarial
Attack class: forge an artifact the gate trusts (command-level masking).
exit 0 = caught, exit 1 = escaped.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixture import (code_repo_with_attacks, push_case,
                     review_with_adversarial_commands, verdict)

repo, sha = code_repo_with_attacks("x1b")
rev = review_with_adversarial_commands(sha, [f"python3 attack{i}.py; true" for i in range(3)])
proc = push_case(repo, rev)

caught = proc.returncode != 0 and "push.probes-adversarial" in proc.stderr
sys.exit(verdict(
    caught,
    f"adversarial cmd `attackN.py; true` (no space); rc={proc.returncode}; "
    f"stderr={proc.stderr.strip()[:300]!r}",
))
