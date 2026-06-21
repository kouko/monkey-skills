#!/usr/bin/env python3
"""golden_compare.py — compare a candidate output to golden anchors for Tier 2 escalation.

When the multi-judge ensemble flags a refactor round as moderate-confidence
(2-of-3 + 1 uncertain), the gate may escalate to Tier 2 by checking whether
the candidate output is closer to a curated golden anchor than the baseline.
This module performs that comparison.

Per references/golden-anchor-protocol.md §How skill-refactor uses goldens.

This script:
    1. Reads golden/ directory for the target skill (frontmatter-tagged
       per golden-anchor-protocol.md schema).
    2. Filters goldens by `prompt_pattern` matching the test prompt.
    3. For each matching golden, computes simple textual similarity
       (word-set Jaccard + length ratio) to baseline output and to
       candidate output.
    4. Emits comparison report.

Note: this is intentionally simple — Jaccard + length is a baseline
heuristic, not a semantic similarity metric. Real semantic similarity
would require LLM judges (which Layer 2 already does). This script
serves the "is candidate at least as close to golden as baseline" check
for Tier 2 escalation, where direction matters more than precision.

Usage:
    python golden_compare.py \\
        --golden-dir <skill>/golden/ \\
        --baseline-output <workspace>/baseline/eval-1/output.md \\
        --candidate-output <workspace>/candidate/eval-1/output.md \\
        --prompt-pattern "user request type" \\
        [--report <output.json>]

Output:
    {
      "matching_goldens": ["golden-1", "golden-3", ...],
      "baseline_avg_similarity": 0.62,
      "candidate_avg_similarity": 0.74,
      "candidate_closer_to_golden": true,
      "verdict": "TIER_2_PASS" | "TIER_2_FAIL"
    }

Exit code: 0 if TIER_2_PASS, 1 if TIER_2_FAIL, 2 on error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Golden parsing
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)
ANCHOR_OUTPUT_RE = re.compile(r"^# Anchor Output\s*\n(.*?)(?=^# |\Z)", re.MULTILINE | re.DOTALL)


def parse_golden(path: Path) -> dict | None:
    """Parse a golden file. Returns dict or None if malformed."""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None

    match = FRONTMATTER_RE.match(text)
    if not match:
        return None

    frontmatter_text = match.group(1)
    body = match.group(2)

    # Naive YAML parse: just lines like `key: value`
    fm: dict = {}
    for line in frontmatter_text.split("\n"):
        if ":" in line and not line.lstrip().startswith("-"):
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()

    # Extract Anchor Output body
    output_match = ANCHOR_OUTPUT_RE.search(body)
    anchor_output = output_match.group(1).strip() if output_match else ""

    return {
        "id": fm.get("id", path.stem),
        "prompt_pattern": fm.get("prompt_pattern", ""),
        "anchor_output": anchor_output,
    }


def load_goldens(golden_dir: Path) -> list[dict]:
    if not golden_dir.exists():
        return []
    goldens = []
    for path in sorted(golden_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        parsed = parse_golden(path)
        if parsed:
            goldens.append(parsed)
    return goldens


# ---------------------------------------------------------------------------
# Similarity metrics
# ---------------------------------------------------------------------------

WORD_RE = re.compile(r"\b\w+\b")


def to_word_set(text: str) -> set[str]:
    return {w.lower() for w in WORD_RE.findall(text)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def length_ratio(a: str, b: str) -> float:
    """Ratio of shorter/longer, in [0, 1]. 1 = same length."""
    la, lb = len(a), len(b)
    if la == 0 and lb == 0:
        return 1.0
    if la == 0 or lb == 0:
        return 0.0
    return min(la, lb) / max(la, lb)


def text_similarity(a: str, b: str) -> float:
    """Combined Jaccard (word set) + length ratio. Equal weight."""
    j = jaccard(to_word_set(a), to_word_set(b))
    lr = length_ratio(a, b)
    return (j + lr) / 2


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------


def filter_goldens_by_pattern(goldens: list[dict], prompt_pattern: str) -> list[dict]:
    """Filter goldens whose prompt_pattern is a substring of the requested pattern (or vice versa).

    Loose matching since prompt_pattern is human-curated free-form text.
    """
    if not prompt_pattern:
        return goldens
    p_lower = prompt_pattern.lower()
    return [
        g for g in goldens
        if p_lower in g["prompt_pattern"].lower() or g["prompt_pattern"].lower() in p_lower
    ]


def compare(golden_dir: Path, baseline_output: str, candidate_output: str, prompt_pattern: str) -> dict:
    goldens = load_goldens(golden_dir)
    if not goldens:
        return {
            "matching_goldens": [],
            "baseline_avg_similarity": None,
            "candidate_avg_similarity": None,
            "candidate_closer_to_golden": None,
            "verdict": "TIER_2_NO_GOLDENS",
            "note": f"no goldens parsed from {golden_dir}; cannot run Tier 2 anchor check",
        }

    matching = filter_goldens_by_pattern(goldens, prompt_pattern)
    if not matching:
        return {
            "matching_goldens": [],
            "baseline_avg_similarity": None,
            "candidate_avg_similarity": None,
            "candidate_closer_to_golden": None,
            "verdict": "TIER_2_NO_MATCH",
            "note": f"no goldens matched prompt_pattern={prompt_pattern!r}; consider adding a matching golden",
        }

    baseline_sims = [text_similarity(baseline_output, g["anchor_output"]) for g in matching]
    candidate_sims = [text_similarity(candidate_output, g["anchor_output"]) for g in matching]

    baseline_avg = sum(baseline_sims) / len(baseline_sims)
    candidate_avg = sum(candidate_sims) / len(candidate_sims)

    closer = candidate_avg >= baseline_avg
    verdict = "TIER_2_PASS" if closer else "TIER_2_FAIL"

    return {
        "matching_goldens": [g["id"] for g in matching],
        "baseline_avg_similarity": round(baseline_avg, 3),
        "candidate_avg_similarity": round(candidate_avg, 3),
        "candidate_closer_to_golden": closer,
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--golden-dir", required=True, type=Path)
    parser.add_argument("--baseline-output", required=True, type=Path)
    parser.add_argument("--candidate-output", required=True, type=Path)
    parser.add_argument("--prompt-pattern", default="")
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    if not args.baseline_output.exists():
        print(f"error: baseline-output does not exist: {args.baseline_output}", file=sys.stderr)
        return 2
    if not args.candidate_output.exists():
        print(f"error: candidate-output does not exist: {args.candidate_output}", file=sys.stderr)
        return 2

    try:
        baseline_text = args.baseline_output.read_text(encoding="utf-8")
        candidate_text = args.candidate_output.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as e:
        print(f"error reading outputs: {e}", file=sys.stderr)
        return 2

    result = compare(args.golden_dir, baseline_text, candidate_text, args.prompt_pattern)
    output = json.dumps(result, indent=2, ensure_ascii=False)

    if args.report:
        args.report.write_text(output, encoding="utf-8")
    else:
        print(output)

    if result["verdict"] == "TIER_2_PASS":
        return 0
    if result["verdict"] in {"TIER_2_NO_GOLDENS", "TIER_2_NO_MATCH"}:
        return 0  # Skipped, not failed
    return 1


if __name__ == "__main__":
    sys.exit(main())
