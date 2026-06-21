#!/usr/bin/env python3
"""score_history.py — track skill-judge scores over time and detect drift.

Optional companion to `skill-judge`. Records per-skill score history
to a JSONL log so subsequent evaluations can detect drift (a
significant drop in score over time) — useful as a regression
signal for skills that have been refactored, retested, or otherwise
modified.

Per the skill-evolution architecture §H3 horizon
(skill-judge drift detection extension).

Score history file location:
    <skill-dir>/.skill-judge-history.jsonl

JSONL entry schema:
    {
        "schema_version": 1,
        "timestamp": "ISO8601 UTC",
        "skill_path": "...",
        "skill_md_hash": "sha256",
        "judge_run_id": "uuid-or-short-id",
        "total_score": 87,
        "letter_grade": "B",
        "dimension_scores": {
            "knowledge_delta": 11,
            "mindset_procedures": 13,
            "anti_pattern": 8,
            "spec_compliance": 14,
            "progressive_disclosure": 12,
            "freedom_calibration": 10,
            "pattern_recognition": 11,
            "practical_usability": 8
        },
        "ear_ratio": "0.55",
        "notes": "..."
    }

Operations:
    append    — record a new evaluation
    query     — list entries for a skill
    drift     — compute drift signal (current vs historical baseline)

Usage:
    python3 score_history.py append <history_file> <entry_json>
    python3 score_history.py query <history_file> [--limit N]
    python3 score_history.py drift <history_file> [--sigma 1.0]

The drift signal:
    - Rolling baseline = mean of historical scores (excluding most recent)
    - Standard deviation = sample stddev of historical scores
    - Drift = (most_recent - baseline) / stddev
    - Flag drift if drift < -sigma (default sigma=1.0)

Exit codes:
    0 — operation succeeded; no drift flagged
    1 — drift flagged (most_recent significantly below baseline)
    2 — error (file missing, malformed log, insufficient history)
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


def load_entries(history_path: Path) -> list[dict[str, Any]]:
    if not history_path.exists():
        return []
    entries = []
    with history_path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"warning: malformed line {lineno}: {e}", file=sys.stderr)
    return entries


def append_entry(history_path: Path, entry: dict[str, Any]) -> None:
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def op_append(history_path: Path, entry_json: str) -> int:
    try:
        entry = json.loads(entry_json)
    except json.JSONDecodeError as e:
        print(f"error: invalid entry JSON: {e}", file=sys.stderr)
        return 2
    if "total_score" not in entry:
        print("error: entry missing 'total_score'", file=sys.stderr)
        return 2
    append_entry(history_path, entry)
    print(f"appended to {history_path}")
    return 0


def op_query(history_path: Path, limit: int | None) -> int:
    entries = load_entries(history_path)
    if limit is not None:
        entries = entries[-limit:]
    for entry in entries:
        ts = entry.get("timestamp", "?")
        score = entry.get("total_score", "?")
        grade = entry.get("letter_grade", "?")
        print(f"{ts}  total={score} grade={grade}")
    return 0


def op_drift(history_path: Path, sigma_threshold: float) -> int:
    entries = load_entries(history_path)
    if len(entries) < 3:
        print(
            f"insufficient history for drift detection: have {len(entries)} "
            f"entries, need ≥3 (1 current + ≥2 baseline samples)",
            file=sys.stderr,
        )
        return 2

    scores = [e.get("total_score") for e in entries if isinstance(e.get("total_score"), (int, float))]
    if len(scores) < 3:
        print(
            f"insufficient numeric scores: have {len(scores)} valid; need ≥3",
            file=sys.stderr,
        )
        return 2

    current = scores[-1]
    baseline = scores[:-1]

    mean = sum(baseline) / len(baseline)
    variance = sum((x - mean) ** 2 for x in baseline) / max(1, len(baseline) - 1)
    stddev = math.sqrt(variance)

    if stddev < 0.5:
        # Effectively constant baseline; absolute drop matters.
        drop = current - mean
        flagged = drop < -1
        z_score = None
    else:
        z_score = (current - mean) / stddev
        flagged = z_score < -sigma_threshold
        drop = current - mean

    report = {
        "n_history": len(scores),
        "baseline_mean": round(mean, 2),
        "baseline_stddev": round(stddev, 2),
        "current_score": current,
        "drop_from_mean": round(drop, 2),
        "z_score": round(z_score, 2) if z_score is not None else None,
        "sigma_threshold": sigma_threshold,
        "drift_flagged": flagged,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if flagged:
        print(
            f"\nDRIFT FLAGGED: current score {current} is below baseline "
            f"({mean:.1f} ± {stddev:.1f}). "
            f"This may indicate subtle quality regression that the "
            f"skill-refactor equivalence check missed. Recommend running "
            f"skill-tuning on this skill to capture human preference signal.",
            file=sys.stderr,
        )
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_app = sub.add_parser("append")
    p_app.add_argument("history_path", type=Path)
    p_app.add_argument("entry_json")

    p_q = sub.add_parser("query")
    p_q.add_argument("history_path", type=Path)
    p_q.add_argument("--limit", type=int, default=None)

    p_d = sub.add_parser("drift")
    p_d.add_argument("history_path", type=Path)
    p_d.add_argument("--sigma", type=float, default=1.0)

    args = parser.parse_args()

    if args.cmd == "append":
        return op_append(args.history_path, args.entry_json)
    if args.cmd == "query":
        return op_query(args.history_path, args.limit)
    if args.cmd == "drift":
        return op_drift(args.history_path, args.sigma)
    return 2


if __name__ == "__main__":
    sys.exit(main())
