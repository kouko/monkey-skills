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

Validation, fail loud, each violation exits non-zero naming the offending
record: top-level JSON must be a list of dicts; each record must have all
required keys (case_id, arm, rep, gating_findings, hedge_marks,
draft_tokens, review_rounds); `arm` must be one of ARMS; every
(case_id, arm, rep) triple must be unique — `rep` is required to be an
int (no int/str coercion) so a triple can't collide by accident; each
gating finding's `cause` must be in the closed A-K set and its `class`
must be "instruction" or "evidence".

The gating-finding metric (registered metric 1 — first-round PREVENTABLE
gating findings) counts only `class: "instruction"` findings;
`class: "evidence"` findings are validated but excluded from every
gating count in the output table.

Output: per-arm totals — first-round gating findings (overall and per
cause, instruction-class only), hedge-mark counts, mean draft tokens,
review rounds — as a markdown table on stdout.

CLI: `python3 prose_selfsweep_tally.py <input.json>`. Stdlib only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

CAUSE_CODES = frozenset("ABCDEFGHIJK")
FINDING_CLASSES = frozenset({"instruction", "evidence"})
ARMS = ("A", "B")
REQUIRED_FIELDS: dict[str, type] = {
    "case_id": str,
    "arm": str,
    "rep": int,
    "gating_findings": list,
    "hedge_marks": int,
    "draft_tokens": int,
    "review_rounds": int,
}


def load_records(path: Path) -> list:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path}: top-level JSON must be a list of records")
    return data


def validate(records: list) -> None:
    """Fail loud, naming the offending record, on: a non-dict record; a
    record missing a required field or with a required field of the wrong
    type; an unknown arm; a non-int `rep` (so a (case_id, arm, rep) triple
    can't collide by int/str type confusion); a duplicate
    (case_id, arm, rep) triple; an unknown gating-finding `cause` code; or
    a gating-finding `class` outside {"instruction", "evidence"}."""
    seen: set[tuple] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"record at index {index}: not a JSON object (dict)")

        for field, expected_type in REQUIRED_FIELDS.items():
            if field not in record:
                raise ValueError(
                    f"record at index {index} ({record!r}): missing required "
                    f"field {field!r}"
                )
            # bool is a subclass of int; reject it explicitly for int fields.
            value = record[field]
            type_ok = isinstance(value, expected_type) and not (
                expected_type is int and isinstance(value, bool)
            )
            if not type_ok:
                raise ValueError(
                    f"record at index {index} ({record!r}): field {field!r} "
                    f"must be {expected_type.__name__}, got {type(value).__name__}"
                )

        case_id = record["case_id"]
        arm = record["arm"]
        rep = record["rep"]

        if arm not in ARMS:
            raise ValueError(
                f"record case_id={case_id!r} rep={rep!r}: "
                f"unknown arm {arm!r} (must be one of {sorted(ARMS)})"
            )

        key = (case_id, arm, rep)
        if key in seen:
            raise ValueError(
                f"duplicate (case_id, arm, rep): {case_id!r}, {arm!r}, {rep!r}"
            )
        seen.add(key)

        for finding in record["gating_findings"]:
            cause = finding.get("cause")
            if cause not in CAUSE_CODES:
                raise ValueError(
                    f"record case_id={case_id!r} arm={arm!r} rep={rep!r}: "
                    f"unknown cause code {cause!r} (must be one of A-K)"
                )
            finding_class = finding.get("class")
            if finding_class not in FINDING_CLASSES:
                raise ValueError(
                    f"record case_id={case_id!r} arm={arm!r} rep={rep!r}: "
                    f"unknown finding class {finding_class!r} "
                    f"(must be one of {sorted(FINDING_CLASSES)})"
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
        # validate() runs before tally() in main() and guarantees arm in
        # ARMS for every record, so no arm-membership guard is needed here.
        bucket = totals[record["arm"]]
        bucket["n_runs"] += 1
        gating_findings = [
            f for f in record["gating_findings"] if f.get("class") == "instruction"
        ]
        bucket["gating_total"] += len(gating_findings)
        for finding in gating_findings:
            bucket["gating_by_cause"][finding["cause"]] += 1
        bucket["hedge_marks_total"] += record["hedge_marks"]
        bucket["draft_tokens"].append(record["draft_tokens"])
        bucket["review_rounds"].append(record["review_rounds"])
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
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
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
