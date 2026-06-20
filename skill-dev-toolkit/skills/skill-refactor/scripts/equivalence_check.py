#!/usr/bin/env python3
"""equivalence_check.py — Layer 1 structural equivalence checker for skill-refactor Q1.

Runs the deterministic structural comparison between baseline and candidate
outputs. Layer 2 (LLM-judge ensemble) lives in multi_judge.py and is
orchestrated separately by the skill's main agent (it needs subagent
spawning, which is environment-specific to Claude Code).

This script handles:
- Output type matching
- Section structure comparison (`## ` headings)
- File path comparison (paths created / referenced)
- Tool call comparison (when tool-call traces are provided)
- Token count delta within ±20%

Per references/equivalence-check-protocol.md §Layer 1.

Usage:
    python equivalence_check.py \\
        --baseline-dir <workspace>/baseline/eval-1/ \\
        --candidate-dir <workspace>/candidate/eval-1/ \\
        [--report <output.json>]

Output:
    JSON report to stdout (or --report path):
        {
            "pass": true | false,
            "checks": {
                "output_type_match": true,
                "section_structure": true,
                "file_paths": true,
                "tool_calls": true,
                "token_count_delta": true
            },
            "details": { ... per-check evidence ... },
            "verdict": "PASS_LAYER_1" | "FAIL_LAYER_1"
        }
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Output type matching
# ---------------------------------------------------------------------------

EXPECTED_TYPES = {".md", ".json", ".csv", ".txt", ".py", ".js", ".ts", ".html"}


def output_types_present(directory: Path) -> set[str]:
    """Return the set of file extensions in a directory."""
    if not directory.exists():
        return set()
    return {p.suffix.lower() for p in directory.rglob("*") if p.is_file()}


def check_output_type_match(baseline_dir: Path, candidate_dir: Path) -> tuple[bool, dict]:
    baseline_types = output_types_present(baseline_dir)
    candidate_types = output_types_present(candidate_dir)
    match = baseline_types == candidate_types
    return match, {
        "baseline_types": sorted(baseline_types),
        "candidate_types": sorted(candidate_types),
        "missing_in_candidate": sorted(baseline_types - candidate_types),
        "extra_in_candidate": sorted(candidate_types - baseline_types),
    }


# ---------------------------------------------------------------------------
# Section structure (markdown only)
# ---------------------------------------------------------------------------

H2_RE = re.compile(r"^##\s+(.+)$", re.MULTILINE)


def extract_h2_set(md_path: Path) -> set[str]:
    if not md_path.exists():
        return set()
    text = md_path.read_text(encoding="utf-8")
    return {h.strip() for h in H2_RE.findall(text)}


def check_section_structure(baseline_dir: Path, candidate_dir: Path) -> tuple[bool, dict]:
    """Compare the union of all `## ` headings in markdown files between dirs.

    Pass: same set of H2 headings (order may vary).
    """
    baseline_md = sorted(baseline_dir.rglob("*.md")) if baseline_dir.exists() else []
    candidate_md = sorted(candidate_dir.rglob("*.md")) if candidate_dir.exists() else []

    baseline_h2 = set()
    for p in baseline_md:
        baseline_h2.update(extract_h2_set(p))

    candidate_h2 = set()
    for p in candidate_md:
        candidate_h2.update(extract_h2_set(p))

    match = baseline_h2 == candidate_h2
    return match, {
        "baseline_h2_count": len(baseline_h2),
        "candidate_h2_count": len(candidate_h2),
        "missing_in_candidate": sorted(baseline_h2 - candidate_h2),
        "extra_in_candidate": sorted(candidate_h2 - baseline_h2),
    }


# ---------------------------------------------------------------------------
# File path set
# ---------------------------------------------------------------------------


def file_paths_relative(directory: Path) -> set[str]:
    if not directory.exists():
        return set()
    return {
        str(p.relative_to(directory))
        for p in directory.rglob("*")
        if p.is_file()
    }


def check_file_paths(baseline_dir: Path, candidate_dir: Path) -> tuple[bool, dict]:
    baseline_paths = file_paths_relative(baseline_dir)
    candidate_paths = file_paths_relative(candidate_dir)
    match = baseline_paths == candidate_paths
    return match, {
        "baseline_count": len(baseline_paths),
        "candidate_count": len(candidate_paths),
        "missing_in_candidate": sorted(baseline_paths - candidate_paths),
        "extra_in_candidate": sorted(candidate_paths - baseline_paths),
    }


# ---------------------------------------------------------------------------
# Tool call comparison (when traces are provided)
# ---------------------------------------------------------------------------


def load_tool_calls(directory: Path) -> list[str]:
    """Read tool_calls.json if present; return list of tool names in invocation order."""
    trace_path = directory / "tool_calls.json"
    if not trace_path.exists():
        return []
    try:
        data = json.loads(trace_path.read_text(encoding="utf-8"))
        return [call.get("tool") for call in data.get("calls", []) if call.get("tool")]
    except (json.JSONDecodeError, AttributeError):
        return []


def check_tool_calls(baseline_dir: Path, candidate_dir: Path) -> tuple[bool, dict]:
    """Compare tool call sequences. Pass if same tool names invoked (count may differ ±1)."""
    baseline_calls = load_tool_calls(baseline_dir)
    candidate_calls = load_tool_calls(candidate_dir)

    if not baseline_calls and not candidate_calls:
        return True, {"note": "no tool_calls.json provided in either dir; skipping check"}

    baseline_set = set(baseline_calls)
    candidate_set = set(candidate_calls)
    set_match = baseline_set == candidate_set
    count_diff = abs(len(baseline_calls) - len(candidate_calls))
    count_within_tolerance = count_diff <= 1

    match = set_match and count_within_tolerance
    return match, {
        "baseline_calls": baseline_calls,
        "candidate_calls": candidate_calls,
        "set_match": set_match,
        "count_diff": count_diff,
        "count_within_tolerance": count_within_tolerance,
    }


# ---------------------------------------------------------------------------
# Token count delta (±20%)
# ---------------------------------------------------------------------------


def total_word_count(directory: Path) -> int:
    """Sum word counts across all text files in directory."""
    if not directory.exists():
        return 0
    total = 0
    for p in directory.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".md", ".txt", ".py", ".js", ".ts", ".html", ".json", ".csv"}:
            try:
                total += len(p.read_text(encoding="utf-8").split())
            except (UnicodeDecodeError, OSError):
                continue
    return total


def check_token_count_delta(baseline_dir: Path, candidate_dir: Path, tolerance: float = 0.20) -> tuple[bool, dict]:
    baseline_words = total_word_count(baseline_dir)
    candidate_words = total_word_count(candidate_dir)

    if baseline_words == 0:
        return False, {"error": "baseline word count is zero; cannot compute delta"}

    delta_pct = abs(candidate_words - baseline_words) / baseline_words
    within = delta_pct <= tolerance

    return within, {
        "baseline_words": baseline_words,
        "candidate_words": candidate_words,
        "delta_pct": round(delta_pct * 100, 1),
        "tolerance_pct": int(tolerance * 100),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run_layer_1(baseline_dir: Path, candidate_dir: Path) -> dict:
    type_pass, type_detail = check_output_type_match(baseline_dir, candidate_dir)
    structure_pass, structure_detail = check_section_structure(baseline_dir, candidate_dir)
    paths_pass, paths_detail = check_file_paths(baseline_dir, candidate_dir)
    tools_pass, tools_detail = check_tool_calls(baseline_dir, candidate_dir)
    tokens_pass, tokens_detail = check_token_count_delta(baseline_dir, candidate_dir)

    all_pass = all([type_pass, structure_pass, paths_pass, tools_pass, tokens_pass])

    return {
        "pass": all_pass,
        "verdict": "PASS_LAYER_1" if all_pass else "FAIL_LAYER_1",
        "checks": {
            "output_type_match": type_pass,
            "section_structure": structure_pass,
            "file_paths": paths_pass,
            "tool_calls": tools_pass,
            "token_count_delta": tokens_pass,
        },
        "details": {
            "output_type_match": type_detail,
            "section_structure": structure_detail,
            "file_paths": paths_detail,
            "tool_calls": tools_detail,
            "token_count_delta": tokens_detail,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--baseline-dir", required=True, type=Path)
    parser.add_argument("--candidate-dir", required=True, type=Path)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    if not args.baseline_dir.exists():
        print(f"error: baseline-dir does not exist: {args.baseline_dir}", file=sys.stderr)
        return 2
    if not args.candidate_dir.exists():
        print(f"error: candidate-dir does not exist: {args.candidate_dir}", file=sys.stderr)
        return 2

    report = run_layer_1(args.baseline_dir, args.candidate_dir)
    output = json.dumps(report, indent=2, ensure_ascii=False)

    if args.report:
        args.report.write_text(output, encoding="utf-8")
    else:
        print(output)

    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
