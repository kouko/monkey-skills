#!/usr/bin/env python3
"""judge_train_stub.py — H4 horizon scaffold for self-trained preference judge.

This is a STUB at v1.7.0. The full training pipeline activates only
when a target skill's preference log has accumulated ≥1000 entries
with ADOPT or DROP verdicts. Until then, this script documents the
interface and fails fast with a clear error.

Per references/self-trained-judge-pipeline.md.

Workflow (when active):
    1. Load preference log; filter by target skill
    2. Extract (preferred, rejected) pairs from ADOPT entries
    3. Pair training: model learns to score preferred > rejected
    4. Evaluate on held-out 20%
    5. Save trained model to <skill>/preference-judge-vN.<ext>
    6. Append a session_summary entry to log noting trainer ran

Workflow (current, v1.7.0):
    Just shouts: "scaffolded, not active. Threshold N=1000 entries.
    Got <K>. Continue using LLM-as-judge."

Usage:
    python judge_train_stub.py \\
        --log /path/to/preference-log.jsonl \\
        --skill <skill-name> \\
        --out /path/to/judge-model.pt \\
        [--min-entries 1000]

Exit codes:
    0 — would have trained (but stub fails)  — never returned in v1.7.0
    1 — insufficient training data (the typical v1.7.0 outcome)
    2 — other error (file missing, malformed log)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_log(log_path: Path) -> list[dict]:
    if not log_path.exists():
        raise FileNotFoundError(f"log not found: {log_path}")
    entries = []
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def extract_preference_pairs(entries: list[dict], skill: str) -> list[dict]:
    """For each ADOPT entry on this skill, generate (preferred, rejected) pairs.

    Each ADOPT becomes one pair per non-picked variant.
    """
    pairs = []
    for e in entries:
        if e.get("skill") != skill:
            continue
        if e.get("verdict") != "ADOPT":
            continue
        picked = e.get("user_pick_identity")
        shown = e.get("variants_shown", [])
        if not picked or not shown:
            continue
        for variant in shown:
            if variant.get("identity") == picked:
                continue
            pairs.append({
                "preferred": picked,
                "rejected": variant.get("identity"),
                "test_prompt_hash": e.get("test_prompt_hash"),
            })
    return pairs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--skill", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--min-entries", type=int, default=1000)
    args = parser.parse_args()

    try:
        entries = load_log(args.log)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    pairs = extract_preference_pairs(entries, args.skill)

    print(f"Skill: {args.skill}")
    print(f"Log: {args.log}")
    print(f"Total log entries: {len(entries)}")
    print(f"Preference pairs (from ADOPT entries): {len(pairs)}")
    print(f"Threshold: ≥{args.min_entries}")

    if len(pairs) < args.min_entries:
        print(
            f"\nInsufficient training data. The self-trained judge pipeline "
            f"is scaffolded but not active. Threshold is "
            f"≥{args.min_entries} preference pairs; you have {len(pairs)}.",
            file=sys.stderr,
        )
        print(
            "\nWhat would happen at threshold:\n"
            "  1. Load all preference pairs from the log (filter on this skill)\n"
            "  2. Split 80/20 train/held-out\n"
            "  3. Train a small preference model (likely a fine-tuned\n"
            "     small LM with Bradley-Terry pairwise loss)\n"
            "  4. Evaluate on held-out set; require ≥80% agreement with\n"
            "     user picks before deploying\n"
            "  5. Compare against generic LLM-as-judge on N=50 fresh\n"
            "     examples; trained judge must outperform\n"
            "  6. If both gates pass: deploy as Tier-1 pre-filter that\n"
            "     ranks variants before showing to user (user still has\n"
            "     final pick)\n"
            "\n"
            "Until then, continue using LLM-as-judge in skill-tasting.\n"
            "See references/self-trained-judge-pipeline.md for the full\n"
            "training methodology, evaluation criteria, deployment\n"
            "model, and privacy / data-handling considerations.\n",
            file=sys.stderr,
        )
        return 1

    # If we ever reach here in a future PR's activated pipeline:
    print(
        f"\nThreshold met ({len(pairs)} ≥ {args.min_entries}) but training "
        f"pipeline activation is not yet implemented. The presence of this "
        f"path indicates {args.skill} has accumulated enough preference data "
        f"that activating real training is now warranted — open a PR to "
        f"replace this stub with the training implementation per the "
        f"methodology in references/self-trained-judge-pipeline.md.",
        file=sys.stderr,
    )
    raise NotImplementedError(
        f"Training pipeline scaffolded but not implemented. Reaching this "
        f"path is itself a signal that activation is now needed: skill "
        f"{args.skill!r} has {len(pairs)} preference pairs (≥ threshold "
        f"{args.min_entries}). Implement training and replace this stub. "
        "Activation methodology: 80/20 train/eval split + Bradley-Terry "
        "preference loss + held-out ≥80% agreement gate + comparison vs "
        "LLM-as-judge baseline."
    )


if __name__ == "__main__":
    sys.exit(main())
