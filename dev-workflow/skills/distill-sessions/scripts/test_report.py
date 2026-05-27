"""test_report.py — tests for report.py (merged.json → advisory markdown renderer).

TDD RED phase: these tests are written BEFORE report.py exists.
Expected initial state: ImportError on 'from report import ...'

Required tests per Task 1 acceptance:
1. test_render_advisory_markdown_includes_required_sections
2. test_parse_merged_json_returns_expected_structure
3. test_cluster_by_title_keyword_groups_similar_titles
4. test_extract_claude_md_candidates_surfaces_cross_target_keywords
5. test_render_handles_empty_input_without_crash
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from report import (
    cluster_by_title_keyword,
    extract_claude_md_candidates,
    parse_merged_json,
    render_advisory_markdown,
)

_SCRIPTS_DIR = Path(__file__).parent
_FIXTURE_PATH = _SCRIPTS_DIR / "fixture_report_merged.json"


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------


def _mk_entry(
    session_id: str,
    target_skill_path: str,
    items: list[dict],
    *,
    kind: str = "failure",
    trajectory_id: str = "traj-1",
) -> dict:
    """Build a minimal merged.json entry."""
    return {
        "session_id": session_id,
        "trajectory_id": trajectory_id,
        "kind": kind,
        "target_skill_path": target_skill_path,
        "memory_items": items,
    }


def _mk_item(title: str, *, description: str = "desc", content: str = "content") -> dict:
    """Build a minimal Memory Item dict."""
    return {
        "title": title,
        "description": description,
        "content": content,
        "kind": "failure",
        "section_anchor": "Examples",
        "requires_new_reference_file": False,
    }


# ---------------------------------------------------------------------------
# Test 1 — required section headings in rendered output.
# ---------------------------------------------------------------------------


def test_render_advisory_markdown_includes_required_sections() -> None:
    """render_advisory_markdown must include all 7 required section headings.

    This is the primary acceptance gate: the report is only useful if all
    sections the user expects are present.
    """
    # Minimal 2-entry merged_data so all sections have something to render.
    merged_data = [
        _mk_entry(
            "session-1",
            "/path/to/brainstorming/SKILL.md",
            [
                _mk_item("AskUserQuestion overuse pattern"),
                _mk_item("Current State Evidence uses memory paths"),
            ],
        ),
        _mk_entry(
            "session-2",
            "/path/to/writing-plans/SKILL.md",
            [
                _mk_item("AskUserQuestion overuse in planning"),
            ],
        ),
    ]

    output = render_advisory_markdown(merged_data, date_str="2026-05-27")

    # H1 title
    assert "# Claude 用法檢討" in output
    # Synthesized-from subtitle
    assert "Synthesized from" in output
    # Section 1: top anti-patterns
    assert "你最常重複的" in output
    # Section 2: per-target skill breakdown
    assert "該改的" in output
    # Section 3: CLAUDE.md candidates
    assert "CLAUDE.md" in output
    # Section 4: new skill candidates
    assert "新 skill 候選" in output
    # Section 5: numbers summary
    assert "數字摘要" in output
    # Section 6: action items
    assert "你現在能做的" in output


# ---------------------------------------------------------------------------
# Test 2 — parse_merged_json returns expected structure from fixture.
# ---------------------------------------------------------------------------


def test_parse_merged_json_returns_expected_structure(tmp_path: Path) -> None:
    """parse_merged_json reads a JSON file and returns a list of dicts.

    Uses a small inline fixture to avoid dependency on the real fixture file
    existing at test time (fixture is bundled in same commit, but test must
    be runnable before it).
    """
    data = [
        _mk_entry(
            "s1",
            "/path/SKILL.md",
            [_mk_item("Title A"), _mk_item("Title B")],
        ),
        _mk_entry(
            "s2",
            "/path2/SKILL.md",
            [_mk_item("Title C")],
        ),
    ]
    fixture = tmp_path / "test_merged.json"
    fixture.write_text(json.dumps(data), encoding="utf-8")

    result = parse_merged_json(str(fixture))

    assert isinstance(result, list), "parse_merged_json must return a list"
    assert len(result) == 2, f"expected 2 entries, got {len(result)}"
    # Each entry has expected keys
    entry = result[0]
    assert "session_id" in entry
    assert "memory_items" in entry
    assert isinstance(entry["memory_items"], list)


def test_parse_merged_json_real_fixture() -> None:
    """parse_merged_json on the real bundled snapshot fixture.

    Verifies: 11 entries, ≥30 total Memory Items, 4 distinct target skills.
    The fixture is bundled alongside this test file.
    """
    if not _FIXTURE_PATH.exists():
        pytest.skip(f"real fixture not yet bundled: {_FIXTURE_PATH}")

    result = parse_merged_json(str(_FIXTURE_PATH))
    assert len(result) == 11, f"expected 11 entries from fixture, got {len(result)}"

    all_items = [item for entry in result for item in entry.get("memory_items", [])]
    assert len(all_items) >= 30, f"expected ≥30 Memory Items, got {len(all_items)}"

    targets = {entry["target_skill_path"] for entry in result}
    assert len(targets) == 4, f"expected 4 distinct target skills, got {len(targets)}"


# ---------------------------------------------------------------------------
# Test 3 — cluster_by_title_keyword groups items with shared keyword.
# ---------------------------------------------------------------------------


def test_cluster_by_title_keyword_groups_similar_titles() -> None:
    """Items sharing a non-stop-word token in their title end up in the same cluster.

    Feed 3 items: 2 share "AskUserQuestion", 1 is unrelated.
    Expect: ≥1 cluster containing both AskUserQuestion items.
    """
    items = [
        _mk_item("AskUserQuestion overuse causes blocking"),
        _mk_item("AskUserQuestion used to avoid recommendation"),
        _mk_item("Current State Evidence cites memory paths"),
    ]

    clusters = cluster_by_title_keyword(items)

    assert isinstance(clusters, dict), "must return dict"
    # Find the cluster containing both AskUserQuestion items.
    ask_cluster = None
    for keyword, cluster_items in clusters.items():
        titles = [it["title"] for it in cluster_items]
        if any("AskUserQuestion" in t for t in titles):
            if len([t for t in titles if "AskUserQuestion" in t]) >= 2:
                ask_cluster = cluster_items
                break

    assert ask_cluster is not None, (
        "Expected ≥1 cluster grouping both AskUserQuestion items together; "
        f"got clusters: {list(clusters.keys())}"
    )
    assert len(ask_cluster) >= 2, (
        f"AskUserQuestion cluster must have ≥2 items, got {len(ask_cluster)}"
    )


def test_cluster_by_title_keyword_does_not_group_unrelated_titles() -> None:
    """Items with no shared non-stop-word keyword stay in separate clusters."""
    items = [
        _mk_item("AskUserQuestion overuse causes blocking"),
        _mk_item("Current State Evidence cites memory paths"),
        _mk_item("Verify files disjoint before parallel dispatch"),
    ]

    clusters = cluster_by_title_keyword(items)

    # Each of the 3 items should end up in separate clusters (no shared keywords).
    # Count total items across all clusters — must be 3 (no duplication).
    all_clustered = [item for cluster_items in clusters.values() for item in cluster_items]
    # Deduplicate by title (union-find may represent shared token across multiple singletons)
    titles_seen = {it["title"] for it in all_clustered}
    assert len(titles_seen) == 3, (
        f"All 3 items must appear exactly once across clusters; titles: {titles_seen}"
    )


# ---------------------------------------------------------------------------
# Test 4 — extract_claude_md_candidates surfaces cross-target keywords.
# ---------------------------------------------------------------------------


def test_extract_claude_md_candidates_surfaces_cross_target_keywords() -> None:
    """Items whose title keyword appears in ≥2 distinct target skills → candidate.

    Feed items across 2 target skills sharing the keyword "AskUserQuestion".
    Expect ≥1 candidate from extract_claude_md_candidates.
    """
    # items_by_target: target_skill_path → list[items]
    items_by_target = {
        "/path/brainstorming/SKILL.md": [
            _mk_item("AskUserQuestion overuse in brainstorming"),
            _mk_item("Current State Evidence cites memory paths"),
        ],
        "/path/writing-plans/SKILL.md": [
            _mk_item("AskUserQuestion blocking writing-plans handoff"),
            _mk_item("Open Questions left for next phase"),
        ],
    }

    candidates = extract_claude_md_candidates(items_by_target)

    assert isinstance(candidates, list), "must return list"
    assert len(candidates) >= 1, (
        "Expected ≥1 CLAUDE.md candidate from cross-target 'AskUserQuestion' keyword; "
        f"got {len(candidates)}"
    )
    # At least one candidate should reference AskUserQuestion (case-insensitive)
    ask_candidates = [
        c for c in candidates
        if "askuserquestion" in c.get("title", "").lower()
        or "askuserquestion" in c.get("keyword", "").lower()
    ]
    assert len(ask_candidates) >= 1, (
        f"Expected AskUserQuestion-related candidate; got candidates: {candidates}"
    )


def test_extract_claude_md_candidates_returns_empty_for_single_target() -> None:
    """No cross-target candidates when all items belong to one skill."""
    items_by_target = {
        "/path/brainstorming/SKILL.md": [
            _mk_item("AskUserQuestion overuse in brainstorming"),
            _mk_item("AskUserQuestion blocks recommendations"),
        ],
    }
    candidates = extract_claude_md_candidates(items_by_target)
    # Single target → no cross-target overlap → empty
    assert candidates == [], (
        f"Single-target items must yield no CLAUDE.md candidates; got {candidates}"
    )


# ---------------------------------------------------------------------------
# Test 5 — empty input does not crash.
# ---------------------------------------------------------------------------


def test_render_handles_empty_input_without_crash() -> None:
    """render_advisory_markdown with empty merged_data must not crash.

    All section headings must still be present even with 0 items — this
    ensures the report shape is consistent regardless of input size.
    """
    output = render_advisory_markdown([], date_str="2026-05-27")

    assert isinstance(output, str)
    assert len(output) > 0, "output must be non-empty even for empty input"

    # All section headings must still appear.
    assert "# Claude 用法檢討" in output
    assert "你最常重複的" in output
    assert "該改的" in output
    assert "CLAUDE.md" in output
    assert "新 skill 候選" in output
    assert "數字摘要" in output
    assert "你現在能做的" in output
