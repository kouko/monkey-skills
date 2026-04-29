#!/usr/bin/env python3
"""preference_log.py — append / query / aggregate skill-tasting preference log entries.

The preference log is a JSONL file at <skill>/preference-log.jsonl.
Each line is one entry per pick or session summary.

Per references/preference-log-schema.md.

Operations:
    append <log_path> <entry_json>
        Append a new entry to the log (atomic, append-only).

    query <log_path> [--skill X] [--session-id Y] [--verdict Z]
        Filter entries by criteria; print to stdout.

    summarize <log_path> [--skill X]
        Per-skill aggregate (total picks, ADOPT rate, etc.).

    export-for-training <log_path> --skill X --out PATH [--min-entries N]
        Export training-ready preference pairs JSON; fails if entries
        below threshold (default 1000).

Usage examples:
    python preference_log.py append /path/to/log.jsonl '{"skill":"X",...}'
    python preference_log.py query /path/to/log.jsonl --skill foo
    python preference_log.py summarize /path/to/log.jsonl --skill foo
    python preference_log.py export-for-training /path/to/log.jsonl --skill foo --out /tmp/training.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------


def load_entries(log_path: Path) -> list[dict[str, Any]]:
    """Read all entries from a JSONL file. Skip malformed lines with a warning."""
    if not log_path.exists():
        return []
    entries = []
    with log_path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"warning: skipping malformed line {lineno}: {e}", file=sys.stderr)
    return entries


def append_entry(log_path: Path, entry: dict[str, Any]) -> None:
    """Atomically append one JSONL entry."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------


def op_append(log_path: Path, entry_json: str) -> int:
    try:
        entry = json.loads(entry_json)
    except json.JSONDecodeError as e:
        print(f"error: invalid entry JSON: {e}", file=sys.stderr)
        return 2
    if not isinstance(entry, dict):
        print(f"error: entry must be a JSON object, got {type(entry).__name__}", file=sys.stderr)
        return 2
    append_entry(log_path, entry)
    print(f"appended to {log_path}")
    return 0


def op_query(log_path: Path, skill: str | None, session_id: str | None, verdict: str | None) -> int:
    entries = load_entries(log_path)
    filtered = entries
    if skill:
        filtered = [e for e in filtered if e.get("skill") == skill]
    if session_id:
        filtered = [e for e in filtered if e.get("session_id") == session_id]
    if verdict:
        filtered = [e for e in filtered if e.get("verdict") == verdict]
    for entry in filtered:
        print(json.dumps(entry, ensure_ascii=False))
    return 0


def op_summarize(log_path: Path, skill: str | None) -> int:
    entries = load_entries(log_path)
    if skill:
        entries = [e for e in entries if e.get("skill") == skill]

    pick_entries = [e for e in entries if e.get("type") != "session_summary" and "verdict" in e]
    summary_entries = [e for e in entries if e.get("type") == "session_summary"]

    verdicts: dict[str, int] = {}
    for e in pick_entries:
        v = e.get("verdict", "unknown")
        verdicts[v] = verdicts.get(v, 0) + 1

    skills_seen = sorted({e.get("skill") for e in entries if e.get("skill")})
    sessions_seen = sorted({e.get("session_id") for e in entries if e.get("session_id")})

    output = {
        "log_path": str(log_path),
        "filter_skill": skill,
        "total_entries": len(entries),
        "pick_entries": len(pick_entries),
        "session_summaries": len(summary_entries),
        "verdicts": verdicts,
        "adopt_rate": (
            verdicts.get("ADOPT", 0) / len(pick_entries) if pick_entries else None
        ),
        "skills_in_log": skills_seen,
        "sessions": sessions_seen,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


def op_export_training(log_path: Path, skill: str, out_path: Path, min_entries: int) -> int:
    entries = load_entries(log_path)
    skill_entries = [e for e in entries if e.get("skill") == skill and e.get("verdict") in {"ADOPT", "DROP"}]

    if len(skill_entries) < min_entries:
        print(
            f"error: insufficient training data for skill {skill!r}: "
            f"got {len(skill_entries)} entries with ADOPT/DROP verdicts, "
            f"need ≥{min_entries}.",
            file=sys.stderr,
        )
        print(
            "Continue using LLM-as-judge in skill-refactor / skill-tasting "
            "until log denser. See "
            "references/self-trained-judge-pipeline.md §When this activates.",
            file=sys.stderr,
        )
        return 1

    pairs: list[dict[str, Any]] = []
    for e in skill_entries:
        if e.get("verdict") == "ADOPT":
            picked = e.get("user_pick_identity")
            shown = {v.get("identity"): v for v in e.get("variants_shown", [])}
            for identity, variant_record in shown.items():
                if identity == picked:
                    continue
                pairs.append({
                    "test_prompt_hash": e.get("test_prompt_hash"),
                    "preferred_skill_md_hash": shown.get(picked, {}).get("skill_md_hash"),
                    "rejected_skill_md_hash": variant_record.get("skill_md_hash"),
                    "evaluator": e.get("evaluator"),
                    "constitution_version": e.get("constitution_version"),
                })

    out = {
        "skill": skill,
        "n_entries_used": len(skill_entries),
        "n_training_pairs": len(pairs),
        "training_pairs": pairs,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"exported {len(pairs)} training pairs to {out_path}")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_append = sub.add_parser("append")
    p_append.add_argument("log_path", type=Path)
    p_append.add_argument("entry_json")

    p_query = sub.add_parser("query")
    p_query.add_argument("log_path", type=Path)
    p_query.add_argument("--skill")
    p_query.add_argument("--session-id")
    p_query.add_argument("--verdict")

    p_sum = sub.add_parser("summarize")
    p_sum.add_argument("log_path", type=Path)
    p_sum.add_argument("--skill")

    p_exp = sub.add_parser("export-for-training")
    p_exp.add_argument("log_path", type=Path)
    p_exp.add_argument("--skill", required=True)
    p_exp.add_argument("--out", required=True, type=Path)
    p_exp.add_argument("--min-entries", type=int, default=1000)

    args = parser.parse_args()

    if args.cmd == "append":
        return op_append(args.log_path, args.entry_json)
    if args.cmd == "query":
        return op_query(args.log_path, args.skill, args.session_id, args.verdict)
    if args.cmd == "summarize":
        return op_summarize(args.log_path, args.skill)
    if args.cmd == "export-for-training":
        return op_export_training(args.log_path, args.skill, args.out, args.min_entries)
    return 2


if __name__ == "__main__":
    sys.exit(main())
