"""report.py — Stage 5c advisory report generator for distill-sessions.

Reads the same ``merged.json`` Stage 4 output as ``propose.py`` and renders a
human-readable zh-TW advisory report at
``docs/skill-mining/<date>-advisory-report.md``.

Pipeline position: Stage 5c (post-propose.py, independent of apply.py).
Input: merged.json produced by main.py Stage 4 cluster step.
Output: a plain-language zh-TW advisory report the user can skim in ~60
seconds, covering:

- Top anti-patterns (title-keyword heuristic cluster)
- Per-target SKILL.md modification breakdown
- CLAUDE.md candidates (keywords appearing across ≥2 target skills)
- 新 skill 候選 placeholder (v0.5+ semantic clustering territory)
- 數字摘要 (trajectory + item counts, target distribution)
- Actionable next steps with effort estimates

The module is **stdlib-only** (preserves v0.1 Q1 lock — no external deps).

CLI::

    python report.py --input merged.json --output docs/skill-mining/2026-05-27-advisory-report.md

If ``--output`` is omitted, defaults to
``docs/skill-mining/<today>-advisory-report.md`` relative to the repo root
(determined as ``<script_dir>/../../../../`` or CWD fallback).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Stop-word list — EN + zh (inline per Q-v0.4.1-3 lock).
# ---------------------------------------------------------------------------

_STOP_WORDS: frozenset[str] = frozenset(
    [
        # EN
        "the",
        "a",
        "an",
        "of",
        "for",
        "and",
        "or",
        "to",
        "in",
        "on",
        "with",
        "when",
        "before",
        "after",
        "not",
        "is",
        "be",
        "are",
        # zh
        "的",
        "了",
        "在",
        "是",
        "不",
        "也",
        "都",
        "而",
        "等",
    ]
)

# Tokenization: split on whitespace + common punctuation.
_TOKEN_SPLIT_RE = re.compile(r"[\s\-\—\:\.\(\),、。；：「」【】]+")


# ---------------------------------------------------------------------------
# Public API.
# ---------------------------------------------------------------------------


def parse_merged_json(path: str) -> list[dict]:
    """Read merged.json from ``path`` and return the list of entries.

    Each entry has keys: ``session_id``, ``trajectory_id``, ``kind``,
    ``target_skill_path``, ``memory_items`` (list of Memory Item dicts).

    Raises ``ValueError`` if the top-level structure is not a list.
    """
    text = Path(path).read_text(encoding="utf-8")
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError(
            f"Expected top-level JSON list in {path}, got {type(data).__name__}"
        )
    return data


def _tokenize_title(title: str) -> set[str]:
    """Tokenize a Memory Item title into a set of meaningful tokens.

    Steps:
    1. Lowercase the title.
    2. Split on whitespace + punctuation (``_TOKEN_SPLIT_RE``).
    3. Strip stop-words.
    4. Drop tokens < 3 chars.

    Returns the resulting token set.
    """
    tokens: set[str] = set()
    for raw in _TOKEN_SPLIT_RE.split(title.lower()):
        tok = raw.strip()
        if len(tok) >= 3 and tok not in _STOP_WORDS:
            tokens.add(tok)
    return tokens


def cluster_by_title_keyword(items: list[dict]) -> dict[str, list[dict]]:
    """Cluster Memory Items by shared title keyword (loose: 1+ non-stop-word token overlap).

    Algorithm: union-find over items. Two items are in the same group when
    their title token sets share ≥1 non-stop-word token of length ≥3.

    Returns dict mapping the first/representative keyword of each group to
    the list of items in that group. Singleton items (no overlap with any
    other item) are still returned as single-element clusters.

    Does not mutate ``items``.
    """
    if not items:
        return {}

    n = len(items)
    token_sets = [_tokenize_title(it["title"]) for it in items]

    # Union-find parent array.
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def _union(x: int, y: int) -> None:
        rx, ry = _find(x), _find(y)
        if rx != ry:
            parent[rx] = ry

    # Pair-wise: union items sharing ≥1 token.
    for i in range(n):
        for j in range(i + 1, n):
            if token_sets[i] & token_sets[j]:
                _union(i, j)

    # Group by root.
    groups: dict[int, list[int]] = {}
    for i in range(n):
        root = _find(i)
        groups.setdefault(root, []).append(i)

    # Build output: representative keyword = highest-frequency shared token
    # among the group's items, or first token of the first item's title.
    result: dict[str, list[dict]] = {}
    for root, indices in groups.items():
        if len(indices) == 1:
            # Singleton — use first non-stop-word token as key.
            tok_set = token_sets[indices[0]]
            rep_key = sorted(tok_set)[0] if tok_set else items[indices[0]]["title"][:20]
        else:
            # Find the shared token(s) most common across the group.
            token_counts: dict[str, int] = {}
            for idx in indices:
                for tok in token_sets[idx]:
                    token_counts[tok] = token_counts.get(tok, 0) + 1
            # Pick token with highest count (tie-break: alphabetical).
            max_count = max(token_counts.values())
            shared_tokens = sorted(
                [t for t, c in token_counts.items() if c == max_count]
            )
            rep_key = shared_tokens[0]
        result[rep_key] = [items[idx] for idx in indices]

    return result


def extract_claude_md_candidates(
    items_by_target: dict[str, list[dict]]
) -> list[dict]:
    """Find Memory Items whose title keywords appear across ≥2 target skills.

    Args:
        items_by_target: mapping from ``target_skill_path`` → list of Memory
            Item dicts.

    Returns a list of candidate dicts:
        ``{"keyword": str, "targets": list[str], "items": list[dict]}``

    A keyword qualifies as a CLAUDE.md candidate if it appears in the title
    token sets of items in ≥2 distinct target skills. False-positives are
    acceptable since the user reviews candidates manually (per Q-v0.4.1-3
    precision/recall trade-off).
    """
    if len(items_by_target) < 2:
        return []

    # Build: keyword → set of target paths where it appears.
    keyword_targets: dict[str, set[str]] = {}
    keyword_items: dict[str, list[dict]] = {}

    for target_path, items in items_by_target.items():
        for item in items:
            for tok in _tokenize_title(item["title"]):
                keyword_targets.setdefault(tok, set()).add(target_path)
                keyword_items.setdefault(tok, []).append(item)

    # Candidates: keywords present in ≥2 targets.
    candidates: list[dict] = []
    seen_keywords: set[str] = set()
    for keyword, targets in sorted(keyword_targets.items()):
        if len(targets) >= 2 and keyword not in seen_keywords:
            seen_keywords.add(keyword)
            candidates.append(
                {
                    "keyword": keyword,
                    "targets": sorted(targets),
                    "items": keyword_items[keyword],
                    # Provide a "title" field so callers can check it directly.
                    "title": keyword,
                }
            )

    return candidates


def _collect_all_items(merged_data: list[dict]) -> list[dict]:
    """Flatten all Memory Items from merged.json entries into one list."""
    flat: list[dict] = []
    for entry in merged_data:
        for item in entry.get("memory_items", []):
            flat.append(item)
    return flat


def _group_items_by_target(merged_data: list[dict]) -> dict[str, list[dict]]:
    """Build target_skill_path → list[item] mapping from merged.json entries."""
    by_target: dict[str, list[dict]] = {}
    for entry in merged_data:
        target = entry.get("target_skill_path", "unknown")
        for item in entry.get("memory_items", []):
            by_target.setdefault(target, []).append(item)
    return by_target


def _short_skill_name(target_skill_path: str) -> str:
    """Extract a short human-readable skill name from a SKILL.md path.

    e.g. '/path/to/brainstorming/SKILL.md' → 'brainstorming'
    """
    p = Path(target_skill_path)
    # SKILL.md → parent dir name = skill name.
    if p.name == "SKILL.md":
        return p.parent.name
    return p.parent.name or p.name


def render_advisory_markdown(merged_data: list[dict], date_str: str) -> str:
    """Render the full zh-TW advisory report markdown as a string.

    Args:
        merged_data: list of merged.json entries (each with ``memory_items``).
        date_str: ``YYYY-MM-DD`` string for the report date header.

    Returns the full markdown document as a string.
    """
    all_items = _collect_all_items(merged_data)
    by_target = _group_items_by_target(merged_data)

    trajectory_count = len(merged_data)
    item_count = len(all_items)
    target_count = len(by_target)

    # --- Cluster by title keyword for anti-pattern section ---
    clusters = cluster_by_title_keyword(all_items)
    # Sort clusters by size descending (largest = most repeated pattern).
    sorted_clusters = sorted(
        clusters.items(), key=lambda kv: len(kv[1]), reverse=True
    )
    # Top patterns: clusters with ≥2 items (actual repeated patterns).
    top_patterns = [(k, v) for k, v in sorted_clusters if len(v) >= 2]

    # --- CLAUDE.md candidates ---
    claude_md_candidates = extract_claude_md_candidates(by_target)

    # --- Build output ---
    lines: list[str] = []

    # H1 title
    lines.append(f"# Claude 用法檢討 — {date_str}")
    lines.append("")

    # Subtitle
    lines.append(
        f"> Synthesized from {trajectory_count} 個 trajectory × "
        f"{item_count} 個 Memory Item，涵蓋 {target_count} 個 target skill。"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Section 1: Top anti-patterns ---
    n_patterns = len(top_patterns)
    lines.append(f"## 你最常重複的 {n_patterns} 個小毛病")
    lines.append("")
    if top_patterns:
        for rank, (keyword, pattern_items) in enumerate(top_patterns, start=1):
            # Show the most representative title (longest, most informative)
            rep_title = max(pattern_items, key=lambda it: len(it.get("title", "")))
            lines.append(f"### #{rank} {rep_title['title']}")
            lines.append(
                f"- 出現 **{len(pattern_items)}** 個 Memory Item 中（關鍵字：`{keyword}`）"
            )
            # List up to 3 titles as evidence.
            evidence_items = pattern_items[:3]
            for it in evidence_items:
                desc = it.get("description", "")
                desc_short = desc[:80] + "…" if len(desc) > 80 else desc
                lines.append(f"  - {it['title']}")
                if desc_short:
                    lines.append(f"    _{desc_short}_")
            if len(pattern_items) > 3:
                lines.append(f"  - _…（共 {len(pattern_items)} 個 item）_")
            lines.append("")
    else:
        lines.append("_(無重複 anti-pattern — 所有 Memory Item title 均唯一)_")
        lines.append("")

    lines.append("---")
    lines.append("")

    # --- Section 2: Per-target SKILL.md breakdown ---
    n_skills = len(by_target)
    n_total_items = item_count
    lines.append(f"## 該改的 {n_skills} 個 skill (共 {n_total_items} 處)")
    lines.append("")
    if by_target:
        for target_path, target_items in sorted(by_target.items()):
            skill_name = _short_skill_name(target_path)
            failure_items = [it for it in target_items if it.get("kind") == "failure"]
            success_items = [it for it in target_items if it.get("kind") == "success"]
            lines.append(f"### {skill_name}（{len(target_items)} 個 item）")
            if failure_items:
                lines.append(f"**改法（{len(failure_items)} 個 failure）：**")
                for it in failure_items:
                    lines.append(f"- {it['title']}")
                    desc = it.get("description", "")
                    if desc:
                        desc_short = desc[:100] + "…" if len(desc) > 100 else desc
                        lines.append(f"  - _{desc_short}_")
            if success_items:
                lines.append(f"**保留（{len(success_items)} 個 success）：**")
                for it in success_items:
                    lines.append(f"- {it['title']}")
            lines.append("")
    else:
        lines.append("_(無 Memory Item)_")
        lines.append("")

    lines.append("---")
    lines.append("")

    # --- Section 3: CLAUDE.md candidates ---
    n_candidates = len(claude_md_candidates)
    lines.append(f"## 該加進 ~/.claude/CLAUDE.md 的 {n_candidates} 條規則")
    lines.append("")
    if claude_md_candidates:
        lines.append("從多個 target skill 重複出現的 pattern 萃取：")
        lines.append("")
        for i, cand in enumerate(claude_md_candidates, start=1):
            keyword = cand["keyword"]
            targets_short = [_short_skill_name(t) for t in cand["targets"]]
            lines.append(f"{i}. **`{keyword}`** — 跨 {len(cand['targets'])} 個 skill: {', '.join(targets_short)}")
            # Show up to 2 representative items.
            rep_items = cand["items"][:2]
            for it in rep_items:
                lines.append(f"   - {it['title']}")
            lines.append("")
    else:
        lines.append("_(無跨 skill 的共通 pattern — 目前所有 Memory Item 屬單一 skill 範疇)_")
        lines.append("")

    lines.append("---")
    lines.append("")

    # --- Section 4: 新 skill 候選 ---
    lines.append("## 新 skill 候選")
    lines.append("")
    lines.append(
        "目前無 — 所有 friction 都有現有 skill 收容 "
        "(v0.5+ semantic clustering ship 後啟用真正的候選偵測)"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Section 5: 數字摘要 ---
    lines.append("## 數字摘要")
    lines.append("")
    lines.append(f"- **Trajectory 數**：{trajectory_count}")
    lines.append(f"- **Memory Item 數**：{item_count}")
    lines.append(f"- **Target skill 數**：{target_count}")
    if by_target:
        lines.append("- **Target 分布**：")
        for target_path, target_items in sorted(by_target.items()):
            skill_name = _short_skill_name(target_path)
            lines.append(f"  - {skill_name}：{len(target_items)} 個 item")
    lines.append("- **費用估算**：見 `main.py` stderr preview（merged.json 不含 session_events 原始 payload，無法在此 re-derive）")
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Section 6: 你現在能做的 N 件事 ---
    action_count = 0
    action_lines: list[str] = []

    if top_patterns:
        action_count += 1
        action_lines.append(
            f"| {action_count}. 把 Top {min(len(top_patterns), 3)} 個 anti-pattern 對應的 SKILL.md edit 手動 apply | ~20–40 分鐘 |"
        )
    if claude_md_candidates:
        action_count += 1
        action_lines.append(
            f"| {action_count}. 把 {n_candidates} 條 CLAUDE.md 規則加進 `~/.claude/CLAUDE.md` | ~5–10 分鐘 |"
        )
    action_count += 1
    action_lines.append(
        f"| {action_count}. 等 v0.5 semantic clustering 出來後 batch processing | 未定 |"
    )
    action_count += 1
    action_lines.append(
        f"| {action_count}. 啥都不做，等下個月再跑一次累積 evidence | 0 分鐘 |"
    )

    lines.append(f"## 你現在能做的 {action_count} 件事")
    lines.append("")
    lines.append("| Action | Effort |")
    lines.append("|---|---|")
    lines.extend(action_lines)
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Entry point for ``python report.py --input ... --output ...``."""
    parser = argparse.ArgumentParser(
        prog="report",
        description=(
            "Stage 5c: read distill-sessions Stage 4 merged.json and render "
            "a zh-TW human-readable advisory report."
        ),
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to merged.json (Stage 4 output from main.py).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Where to write the advisory report markdown. "
            "Default: docs/skill-mining/<today>-advisory-report.md "
            "relative to repo root."
        ),
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Override date string (YYYY-MM-DD); default = today.",
    )
    args = parser.parse_args(argv)

    date_str = args.date or date.today().isoformat()

    merged_data = parse_merged_json(str(args.input))

    output_path: Path
    if args.output is not None:
        output_path = args.output
    else:
        # Default: docs/skill-mining/<date>-advisory-report.md
        # Try to resolve from script location (4 levels up to repo root).
        script_dir = Path(__file__).resolve().parent
        repo_root = script_dir.parents[3]  # scripts/ → distill-sessions/ → skills/ → dev-workflow/ → repo root
        output_path = repo_root / "docs" / "skill-mining" / f"{date_str}-advisory-report.md"

    output = render_advisory_markdown(merged_data, date_str=date_str)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")
    print(f"wrote {output_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":  # pragma: no cover  (CLI entrypoint)
    sys.exit(main())
