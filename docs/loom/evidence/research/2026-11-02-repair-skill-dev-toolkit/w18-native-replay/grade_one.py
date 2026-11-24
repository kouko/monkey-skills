#!/usr/bin/env python3
"""Grade a W18 replay run against the preregistered grading spec.

Mechanical clauses (1 labels, 3 controls) are checked exactly. Clause 2
(reason fidelity for F1) is flagged for human inspection: the grader prints
the F1 reason and the three failure subclauses, and records PASS/FAIL verdicts
it cannot compute itself.

Usage: grade_one.py <trial|run-2|run-3>
"""
import hashlib
import json
import pathlib
import sys

WORK = pathlib.Path("/private/tmp/toolkit-w18-replay-20261124")
TOOLS = pathlib.Path("/private/tmp/toolkit-w18-replay-20261124-tools")
RUN = sys.argv[1]
run_dir = WORK / "runs" / RUN
INPUTS = WORK / "inputs"

results = {"run": RUN, "mechanical": {}, "clause2": None, "pass_mechanical": True}

# --- Clause 1 & 3: labels ---
CASES = {"original": "original", "case-k": "case-k", "case-m": "case-m"}
INPUT_CASES = {"original": "original", "case-k": "holdouts/case-k", "case-m": "holdouts/case-m"}
orig = json.loads((run_dir / "original" / "decisions.json").read_text())
k = json.loads((run_dir / "case-k" / "decisions.json").read_text())
m = json.loads((run_dir / "case-m" / "decisions.json").read_text())

def status_of(dd, source, fid):
    for d in dd["decisions"]:
        if d["source"] == source and d["id"] == fid:
            return d["status"]
    return "MISSING"

f1 = status_of(orig, "read-1.json", "F1")
results["mechanical"]["F1_label"] = f1
results["mechanical"]["F1_ok"] = f1 == "excluded"
k1 = status_of(k, "read-1.json", "HOLDOUT-K1")
results["mechanical"]["K1_label"] = k1
results["mechanical"]["K1_ok"] = k1 == "excluded"
m1 = status_of(m, "read-1.json", "HOLDOUT-M1")
results["mechanical"]["M1_label"] = m1
results["mechanical"]["M1_ok"] = m1 == "confirmed"

# Byte preservation of raw inputs (mechanical antecedent)
for case, input_subdir in INPUT_CASES.items():
    for name in ("read-1.json", "simulate-1.json"):
        src = (INPUTS / input_subdir / name).read_bytes()
        dst = (run_dir / CASES[case] / name).read_bytes()
        ok = hashlib.sha256(src).hexdigest() == hashlib.sha256(dst).hexdigest()
        results["mechanical"][f"raw_bytes_{case}_{name}"] = ok
        results["pass_mechanical"] = results["pass_mechanical"] and ok

results["pass_mechanical"] = results["pass_mechanical"] and all(
    results["mechanical"][x] for x in ("F1_ok", "K1_ok", "M1_ok")
)

# --- Clause 2: print F1 reason for human grading ---
f1_reason = next(
    (d["reason"] for d in orig["decisions"] if d["source"] == "read-1.json" and d["id"] == "F1"),
    "",
)
results["clause2_f1_reason"] = f1_reason

# Mechanical F1-reason red flags (advisory only; human decides)
flags = []
low = f1_reason.lower()
if "all prose" in low or "every prose" in low:
    flags.append("asserts all/every prose")
if "outside entry scope" in low:
    flags.append("outside-entry-scope claim")
results["clause2_red_flags"] = flags

(TOOLS / f"{RUN}.grade.json").write_text(json.dumps(results, indent=2) + "\n")
print(json.dumps({k2: v for k2, v in results.items() if k2 != "clause2_f1_reason"}, indent=1))
print("\n--- F1 reason (for clause-2 human grading) ---")
print(f1_reason)
