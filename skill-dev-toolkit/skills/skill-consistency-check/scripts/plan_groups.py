#!/usr/bin/env python3
"""Decide whether a skill package is read whole or in groups.

Usage: python3 plan_groups.py <skill_dir>

Thresholds are fixed: LIMIT (30,000 tokens) and GROUP_MAX (25,000 tokens).
Prints one JSON object to stdout and writes no files. Exit 0 on success,
2 on error (bad path or no SKILL.md). Python 3 stdlib only.
"""

import argparse
import itertools
import json
import math
import re
import sys
from pathlib import Path

CJK_RE = re.compile(
    "["
    "ᄀ-ᇿ"  # Hangul Jamo
    "　-〿"  # CJK symbols and punctuation
    "぀-ゟ"  # Hiragana
    "゠-ヿ"  # Katakana
    "㄰-㆏"  # Hangul compatibility Jamo
    "㐀-䶿"  # CJK Unified Ideographs Extension A
    "一-鿿"  # CJK Unified Ideographs
    "가-힯"  # Hangul syllables
    "＀-￯"  # Halfwidth and fullwidth forms
    "]"
)
README_RE = re.compile(r"^README(\..+)?\.md$")
LIMIT = 30000
GROUP_MAX = 25000


def estimate_tokens(text):
    # CJK chars count one each; the rest is words x 1.33, the estimator that
    # produced the agreed 30k / 25k thresholds.
    cjk = len(CJK_RE.findall(text))
    words = len(CJK_RE.sub(" ", text).split())
    return cjk + math.ceil(1.33 * words)


def package_files(root):
    paths = []
    for p in root.rglob("*.md"):
        if p.is_file() and not README_RE.match(p.name):
            paths.append(p.relative_to(root).as_posix())
    return sorted(paths)


def chunk(periphery, tokens, budget):
    chunks, current, used = [], [], 0
    for path in periphery:
        t = tokens[path]
        if current and used + t > budget:
            chunks.append(current)
            current, used = [], 0
        current.append(path)
        used += t
    if current:
        chunks.append(current)
    return chunks


def named_in(path, text):
    """True when path appears in text on path boundaries (data.md ≠ a.md)."""
    pattern = r"(?<![\w./-])" + re.escape(path) + r"(?![\w/-])"
    return re.search(pattern, text) is not None


def grouped_plan(core, periphery, tokens, budget):
    """Offset read/simulate groups and the periphery pairs never co-grouped."""
    read_chunks = chunk(periphery, tokens, budget)
    k = max(1, len(read_chunks[0]) // 2)
    rotated = periphery[k:] + periphery[:k]
    sim_chunks = chunk(rotated, tokens, budget)
    covered = set()
    for c in read_chunks + sim_chunks:
        covered.update(itertools.combinations(sorted(c), 2))
    uncovered = [
        [a, b]
        for a, b in itertools.combinations(periphery, 2)
        if (a, b) not in covered
    ]
    return [core + c for c in read_chunks], [core + c for c in sim_chunks], uncovered


def build_plan(root):
    paths = package_files(root)
    texts = {p: (root / p).read_text(encoding="utf-8", errors="replace") for p in paths}
    tokens = {p: estimate_tokens(texts[p]) for p in paths}
    skill_text = texts.get("SKILL.md", "")
    core_set = {
        p
        for p in paths
        if p == "SKILL.md" or p.startswith("agents/") or named_in(p, skill_text)
    }
    core = [p for p in paths if p in core_set]
    periphery = [p for p in paths if p not in core_set]
    total = sum(tokens.values())
    core_tokens = sum(tokens[p] for p in core)
    grouped = total > LIMIT

    if not grouped:
        read = simulate = [list(paths)]
        uncovered = []
    elif not periphery:
        read = simulate = [list(core)]
        uncovered = []
    else:
        read, simulate, uncovered = grouped_plan(
            core, periphery, tokens, GROUP_MAX - core_tokens
        )

    return {
        "target": str(root),
        "limit": LIMIT,
        "group_max": GROUP_MAX,
        "files": [{"path": p, "tokens": tokens[p], "core": p in core_set} for p in paths],
        "total_tokens": total,
        "core_tokens": core_tokens,
        "grouped": grouped,
        "over_limit": grouped
        and any(sum(tokens[p] for p in g) > GROUP_MAX for g in read + simulate),
        "groups": {"read": read, "simulate": simulate},
        "uncovered_pairs": uncovered,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("skill_dir")
    args = parser.parse_args(argv)
    root = Path(args.skill_dir).resolve()
    if not root.is_dir():
        print(f"plan_groups: not a directory: {args.skill_dir}", file=sys.stderr)
        return 2
    if not (root / "SKILL.md").is_file():
        print(f"plan_groups: no SKILL.md in {args.skill_dir}; not a skill folder", file=sys.stderr)
        return 2
    print(json.dumps(build_plan(root), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
