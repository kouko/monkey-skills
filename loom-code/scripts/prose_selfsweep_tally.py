#!/usr/bin/env python3
"""Tally A/B prose-self-sweep run records into a markdown table.

Scores only — no verdict, no "improved"/"worse" wording. Interpretation
of the numbers stays a human judgment made elsewhere (see
docs/loom/plans/2026-09-01-prose-edit-self-sweep.md Task 3).

Input: a JSON file holding a list of records, one per run:

    {
        "case_id": str,
        "arm": "A" | "B",
        "rep": int,
        "gating_findings": [{"cause": "A".."K", "class": "instruction" | "evidence"}],
        "hedge_marks": int,
        "draft_tokens": int,
        "review_rounds": int,
    }

Validation, fail loud: every `cause` must be in the closed A-K set; every
(case_id, arm, rep) triple must be unique. Either violation exits non-zero
naming the offending record.

Output: per-arm totals — first-round gating findings (overall and per
cause), hedge-mark counts, mean draft tokens, review rounds — as a
markdown table on stdout.

CLI: `python3 prose_selfsweep_tally.py <input.json>`. Stdlib only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

CAUSE_CODES = frozenset("ABCDEFGHIJK")
ARMS = ("A", "B")


def load_records(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path}: top-level JSON must be a list of records")
    return data


def validate(records: list[dict]) -> None:
    """Fail loud on an unknown cause code or a duplicate (case_id, arm,
    rep) triple, naming the offending record in the message."""
    seen: set[tuple] = set()
    for record in records:
        case_id = record.get("case_id")
        arm = record.get("arm")
        rep = record.get("rep")
        key = (case_id, arm, rep)
        if key in seen:
            raise ValueError(
                f"duplicate (case_id, arm, rep): {case_id!r}, {arm!r}, {rep!r}"
            )
        seen.add(key)

        for finding in record.get("gating_findings", []):
            cause = finding.get("cause")
            if cause not in CAUSE_CODES:
                raise ValueError(
                    f"record case_id={case_id!r} arm={arm!r} rep={rep!r}: "
                    f"unknown cause code {cause!r} (must be one of A-K)"
                )


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def tally(records: list[dict]) -> dict[str, dict]:
    """Per-arm totals: overall + per-cause first-round gating-finding
    counts, hedge-mark totals, mean draft tokens, mean review rounds."""
    totals: dict[str, dict] = {
        arm: {
            "n_runs": 0,
            "gating_total": 0,
            "gating_by_cause": {c: 0 for c in sorted(CAUSE_CODES)},
            "hedge_marks_total": 0,
            "draft_tokens": [],
            "review_rounds": [],
        }
        for arm in ARMS
    }
    for record in records:
        arm = record.get("arm")
        if arm not in totals:
            continue
        bucket = totals[arm]
        bucket["n_runs"] += 1
        findings = record.get("gating_findings", [])
        bucket["gating_total"] += len(findings)
        for finding in findings:
            bucket["gating_by_cause"][finding["cause"]] += 1
        bucket["hedge_marks_total"] += record.get("hedge_marks", 0)
        bucket["draft_tokens"].append(record.get("draft_tokens", 0))
        bucket["review_rounds"].append(record.get("review_rounds", 0))
    return totals


def render_table(totals: dict[str, dict]) -> str:
    lines = [
        "| metric | " + " | ".join(ARMS) + " |",
        "| --- | " + " | ".join("---" for _ in ARMS) + " |",
        "| runs | " + " | ".join(str(totals[a]["n_runs"]) for a in ARMS) + " |",
        "| gating findings (total) | "
        + " | ".join(str(totals[a]["gating_total"]) for a in ARMS) + " |",
    ]
    for cause in sorted(CAUSE_CODES):
        lines.append(
            f"| gating findings (cause {cause}) | "
            + " | ".join(str(totals[a]["gating_by_cause"][cause]) for a in ARMS)
            + " |"
        )
    lines.append(
        "| hedge marks (total) | "
        + " | ".join(str(totals[a]["hedge_marks_total"]) for a in ARMS) + " |"
    )
    lines.append(
        "| draft tokens (mean) | "
        + " | ".join(f"{_mean(totals[a]['draft_tokens']):.1f}" for a in ARMS) + " |"
    )
    lines.append(
        "| review rounds (mean) | "
        + " | ".join(f"{_mean(totals[a]['review_rounds']):.1f}" for a in ARMS) + " |"
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: prose_selfsweep_tally.py <input.json>", file=sys.stderr)
        return 2

    path = Path(argv[0])
    try:
        records = load_records(path)
    except OSError as exc:
        print(f"cannot read {path}: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"{path}: invalid JSON: {exc}", file=sys.stderr)
        return 1

    try:
        validate(records)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    totals = tally(records)
    print(render_table(totals), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
