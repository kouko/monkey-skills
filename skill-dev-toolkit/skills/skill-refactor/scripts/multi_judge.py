#!/usr/bin/env python3
"""multi_judge.py — Layer 2 LLM-judge ensemble orchestrator for skill-refactor Q1.

This module documents the 3-judge ensemble protocol and provides utilities
for aggregating ensemble results. The actual judge calls are spawned by the
skill's main agent via Claude Code's Task tool — Python alone cannot reach
those subagents — so this script handles consensus aggregation and report
formatting, not the judge invocation itself.

Per references/multi-judge-ensemble.md.

Workflow:
    1. Main agent spawns 3 Task subagents (one per judge frame:
       utility / content / boundary).
    2. Each subagent receives the prompt + outputs labeled A / B
       (random assignment) and returns a verdict JSON.
    3. Main agent collects results into ensemble.json.
    4. This script reads ensemble.json and emits the consensus verdict
       per references/equivalence-check-protocol.md §Layer 2.

ensemble.json schema:
    {
      "judges": [
        {
          "judge_id": 1,
          "frame": "utility",
          "a_is": "baseline" | "candidate",
          "b_is": "candidate" | "baseline",
          "verdict": "equivalent" | "not_equivalent" | "uncertain",
          "reason": "1-2 sentence reason"
        },
        ...
      ]
    }

Usage:
    python multi_judge.py --ensemble <path/to/ensemble.json>

Output to stdout:
    {
      "consensus": "PASS_HIGH" | "PASS_MODERATE" | "FLAG_TIER_2" | "FAIL",
      "verdict_counts": {"equivalent": N, "not_equivalent": M, "uncertain": K},
      "specific_diff_dissent": true | false,
      "reasoning": "..."
    }

Exit code: 0 if PASS_HIGH or PASS_MODERATE, 2 if FLAG_TIER_2, 1 if FAIL.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Literal

VerdictType = Literal["equivalent", "not_equivalent", "uncertain"]
ConsensusType = Literal["PASS_HIGH", "PASS_MODERATE", "FLAG_TIER_2", "FAIL"]


# ---------------------------------------------------------------------------
# Specific-behavior-diff detector
# ---------------------------------------------------------------------------

# Phrases in a judge's reason that indicate specific behavior change rather
# than vague taste. If a `not_equivalent` reason matches any of these, the
# specific-diff override fires (regardless of numeric majority).
SPECIFIC_DIFF_PATTERNS = [
    r"\bskip\w*\s+(?:a|the|this|that)?\s*(?:check|step|validation|case)",
    r"\bdrop\w*\s+(?:a|the|this|that)?\s*(?:warning|fallback|edge|mention|reference)",
    r"\b(?:no|missing|absent|removed)\s+(?:fallback|warning|edge case|reference|invariant)",
    r"\b(?:different|changed|altered)\s+(?:format|contract|input|output)",
    r"\bdoesn'?t\s+(?:handle|cover|address|process)",
    r"\bfails to\b",
    r"\bbehavior\s+(?:change|diff|differ)",
    r"\b(?:specific|specific\s+to)\s+(?:edge|boundary|fallback)",
]


def reason_cites_specific_diff(reason: str) -> bool:
    if not reason:
        return False
    lower = reason.lower()
    return any(re.search(pattern, lower) for pattern in SPECIFIC_DIFF_PATTERNS)


# ---------------------------------------------------------------------------
# Consensus rules
# ---------------------------------------------------------------------------


def aggregate_ensemble(judges: list[dict]) -> dict:
    """Apply consensus rules per references/equivalence-check-protocol.md."""
    if len(judges) != 3:
        return {
            "consensus": "FAIL",
            "verdict_counts": {},
            "specific_diff_dissent": False,
            "reasoning": f"expected exactly 3 judges, got {len(judges)}",
        }

    counts: dict[str, int] = {"equivalent": 0, "not_equivalent": 0, "uncertain": 0}
    for j in judges:
        v = j.get("verdict")
        if v in counts:
            counts[v] += 1
        else:
            counts.setdefault("invalid", 0)
            counts["invalid"] += 1

    if counts.get("invalid"):
        return {
            "consensus": "FAIL",
            "verdict_counts": counts,
            "specific_diff_dissent": False,
            "reasoning": "one or more judges returned invalid verdict; gate cannot proceed",
        }

    # Specific-diff dissent override: if any not_equivalent reason cites
    # a specific behavior diff, this outranks numeric majority.
    specific_diff_dissent = any(
        j.get("verdict") == "not_equivalent" and reason_cites_specific_diff(j.get("reason", ""))
        for j in judges
    )

    eq, neq, unc = counts["equivalent"], counts["not_equivalent"], counts["uncertain"]

    if specific_diff_dissent and eq < 3:
        consensus: ConsensusType = "FLAG_TIER_2"
        reasoning = "specific-behavior-diff dissent overrides numeric majority"
    elif eq == 3:
        consensus = "PASS_HIGH"
        reasoning = "3/3 judges agree equivalent"
    elif eq == 2 and unc == 1:
        consensus = "PASS_MODERATE"
        reasoning = "2/3 equivalent + 1 uncertain (no concrete dissent)"
    elif eq == 2 and neq == 1:
        consensus = "FLAG_TIER_2"
        reasoning = "2/3 equivalent but 1 dissents → escalate to human"
    elif eq <= 1:
        consensus = "FAIL"
        reasoning = "≤1 judge agrees equivalent; refactor not behavior-preserving"
    else:
        consensus = "FAIL"
        reasoning = f"unexpected vote distribution: {counts}"

    return {
        "consensus": consensus,
        "verdict_counts": counts,
        "specific_diff_dissent": specific_diff_dissent,
        "reasoning": reasoning,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--ensemble", required=True, type=Path,
                        help="Path to ensemble.json with 3 judge results")
    args = parser.parse_args()

    if not args.ensemble.exists():
        print(f"error: ensemble file does not exist: {args.ensemble}", file=sys.stderr)
        return 2

    try:
        data = json.loads(args.ensemble.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON in ensemble file: {e}", file=sys.stderr)
        return 2

    judges = data.get("judges", [])
    result = aggregate_ensemble(judges)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    consensus = result["consensus"]
    if consensus in {"PASS_HIGH", "PASS_MODERATE"}:
        return 0
    if consensus == "FLAG_TIER_2":
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
