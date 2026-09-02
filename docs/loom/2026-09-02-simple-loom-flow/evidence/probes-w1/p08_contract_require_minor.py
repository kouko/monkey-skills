#!/usr/bin/env python3
"""P08 — a consumer plugin declares a requires-contract floor HIGHER than
the shipped manifest minor (loom-design says 1.9, loom-code ships 1.0).

TARGET RULE: contract.requires
Attack class: replay a stale artifact / cross a version boundary.
exit 0 = caught (all three over-floors blocked, the met one passes),
exit 1 = escaped.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixture import checker, new_repo, verdict

repo = new_repo("p08")

cases = {
    "1.9": "block",   # same major, minor floor unmet
    "2.0": "block",   # higher major
    "0.9": "block",   # stale consumer major
    "1.0": "pass",    # exactly met
}
results = {}
ok = True
for want, expect in cases.items():
    proc = checker(repo, "contract", "--require", want)
    if proc.returncode == 0:
        got = "pass"
    elif "contract.requires" in proc.stderr:
        got = "block"
    else:
        got = "block-wrong-rule"
    results[want] = (got, proc.stdout.strip()[:80] or proc.stderr.strip()[:120])
    if got != expect:
        ok = False

sys.exit(verdict(ok, f"{results}"))
