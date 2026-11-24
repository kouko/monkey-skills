#!/usr/bin/env python3
"""Emit the W18 replay archive JSON (immutable experimental evidence).

Copies the per-run decision sets, verdicts, usage and request records into one
JSON file under docs/loom/<change>/evidence/. Reads only the replay workspace;
writes only the archive file.
"""
import hashlib
import json
import pathlib

WORK = pathlib.Path("/private/tmp/toolkit-w18-replay-20261124")
TOOLS = pathlib.Path("/private/tmp/toolkit-w18-replay-20261124-tools")
OUT = pathlib.Path(
    "/Users/kouko/GitHub/monkey-skills/docs/loom/2026-11-02-repair-skill-dev-toolkit/evidence/"
    "w18-native-replays.json"
)

RUNS = ["trial", "run-2", "run-3"]
CASES = ["original", "case-k", "case-m"]

archive = {
    "purpose": "W18 per-candidate-isolation native replay evidence; immutable, not a product schema",
    "recorded": "2026-11-24",
    "authorization": "user OK 2026-11-24: three native replays, gpt-6.1-sol/high, same frozen input, first repeat vetoes",
    "runtime_commit": "9b76c250fa15c77f76fe0339b3f6016f4cba344e",
    "runtime_scope": "skill-dev-toolkit/skills/skill-consistency-check (git archive)",
    "inputs_source": "rebuilt from w17-scope-first-results.json input_preimages; 93 files SHA256-verified",
    "inputs_verification": {"files_verified": 93, "mismatches": 0},
    "preregistration": {
        "written_before_results": True,
        "veto": "original read-1.json F1 must be excluded; confirmed is the W17 overbroad false positive",
        "reason_fidelity": "F1 reason must keep any parenthetical/example within its source-assigned category and scope",
        "controls": "case-k HOLDOUT-K1 excluded; case-m HOLDOUT-M1 confirmed",
        "other_candidates": "no gold label; recorded, not graded",
    },
    "runs": {},
    "divergences": {
        "simulate-1.json F1": {
            "w18": ["confirmed", "confirmed", "confirmed"],
            "w17": ["excluded", "excluded", "excluded"],
            "status": "not covered by veto rule; blind audits dispatched",
        },
        "read-1.json F2": {
            "w18": ["excluded", "confirmed", "excluded"],
            "w17": ["excluded", "excluded", "excluded"],
            "status": "cross-run instability; blind audits dispatched",
        },
        "simulate-1.json F3": {
            "w18": ["excluded", "confirmed", "excluded"],
            "w17": ["excluded", "excluded", "excluded"],
            "status": "cross-run instability; blind audits dispatched",
        },
    },
    "limits": [
        "not accuracy testing; not a healed-Claude claim; not cross-model validation; not release approval",
        "requested model identity not observed by the executor JSONL; merger called with --model unknown",
        "one frozen original fixture plus two controls; does not establish general caller correctness",
        "W17 rejection and its three executions remain unchanged; W18 continues the same task without resetting counters",
    ],
}

total_cost = 0.0
for run in RUNS:
    summary = json.loads((TOOLS / f"{run}.summary.json").read_text())
    total_cost += summary["api_equivalent_estimate_usd"]
    request = json.loads((TOOLS / f"{run}.request.json").read_text())
    entry = {
        "exit_code": summary["exit_code"],
        "complete": summary["complete"],
        "elapsed_seconds": summary["elapsed_seconds"],
        "tool_calls": summary["tool_calls"],
        "usage": summary["usage"],
        "api_equivalent_estimate_usd": summary["api_equivalent_estimate_usd"],
        "requested_model": summary["requested_model"],
        "requested_effort": summary["requested_effort"],
        "actual_backend_identity": summary["actual_backend_identity"],
        "packet_sha256": request["packet_sha256"],
        "cases": {},
    }
    for case in CASES:
        ddir = WORK / "runs" / run / case
        decisions = json.loads((ddir / "decisions.json").read_text())
        report = json.loads((ddir / "consistency-report.json").read_text())
        raws = {}
        for name in ("read-1.json", "simulate-1.json"):
            raws[name] = hashlib.sha256((ddir / name).read_bytes()).hexdigest()
        entry["cases"][case] = {
            "verdict": report.get("verdict"),
            "counts": report.get("counts"),
            "decisions": [
                {"source": d["source"], "id": d["id"], "status": d["status"], "reason": d["reason"]}
                for d in decisions["decisions"]
            ],
            "raw_sha256": raws,
        }
    archive["runs"][run] = entry

archive["total_estimate_usd"] = round(total_cost, 4)
OUT.write_text(json.dumps(archive, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {OUT} ({OUT.stat().st_size} bytes); total ${archive['total_estimate_usd']}")
