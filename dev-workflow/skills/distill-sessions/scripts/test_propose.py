"""test_propose.py — tests for propose.py (merge subagent outputs → diff renderer).

Per Plan Part 2 §Task 7 acceptance:
1. test_merge_dedups_near_identical_memory_items — Title-key match + content
   overlap (SequenceMatcher ratio ≥ 0.85) collapses two near-identical items.
2. test_requires_new_reference_file_routes_to_v02_bucket — items flagged
   `requires_new_reference_file: true` appear in §"Marked for v0.2", NOT in
   the main diff (additions / modifications).
3. test_unified_diff_block_per_modification — output markdown contains fenced
   ```diff blocks with `+ ` / `- ` lines per modification proposal.
4. test_snapshot_matches_expected_output — given fixture_subagent_results.json,
   propose.py writes a proposals.md whose normalized content matches the
   committed fixture_expected_proposals.md baseline.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from propose import (
    dedup_items,
    extract_memory_items,
    normalize_memory_item,
    partition_by_v02_marker,
    render_proposals_markdown,
)


_SCRIPTS_DIR = Path(__file__).parent
_FIXTURE_INPUT = _SCRIPTS_DIR / "fixture_subagent_results.json"
_FIXTURE_EXPECTED = _SCRIPTS_DIR / "fixture_expected_proposals.md"


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------


def _mk_item(
    title: str,
    *,
    description: str = "desc",
    content: str = "content",
    kind: str = "failure",
    section_anchor: str = "Examples",
    requires_new_reference_file: bool = False,
) -> dict:
    return {
        "title": title,
        "description": description,
        "content": content,
        "kind": kind,
        "section_anchor": section_anchor,
        "requires_new_reference_file": requires_new_reference_file,
    }


def _normalize_markdown(text: str) -> str:
    """Strip trailing whitespace and normalize dates for snapshot comparison."""
    # Replace any ISO date in headers / file paths with a placeholder.
    text = re.sub(r"\d{4}-\d{2}-\d{2}", "YYYY-MM-DD", text)
    # Strip trailing whitespace per-line.
    return "\n".join(line.rstrip() for line in text.splitlines()).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Test 1 — dedup.
# ---------------------------------------------------------------------------


def test_merge_dedups_near_identical_memory_items() -> None:
    """Two Memory Items with very similar Title + content collapse to 1."""
    items = [
        _mk_item(
            "Avoid calling Bash for git commands",
            content="Use the Git tool instead of Bash for git operations.",
        ),
        _mk_item(
            "Avoid calling Bash for git commands.",
            content="Use the Git tool instead of Bash for git ops.",
        ),
    ]
    deduped = dedup_items(items)
    assert len(deduped) == 1, "near-identical titles + content should merge"


def test_dedup_keeps_distinct_items_different_titles() -> None:
    """Two items with clearly different Titles do NOT merge."""
    items = [
        _mk_item("Avoid calling Bash for git commands", content="Use Git tool."),
        _mk_item("Use Read before Edit", content="Read tool tracks file state."),
    ]
    deduped = dedup_items(items)
    assert len(deduped) == 2, "different titles must stay distinct"


# ---------------------------------------------------------------------------
# Test 2 — v0.2 bucket routing.
# ---------------------------------------------------------------------------


def test_requires_new_reference_file_routes_to_v02_bucket(tmp_path: Path) -> None:
    """Items flagged `requires_new_reference_file: true` go to §Marked for v0.2,
    NOT into Proposed additions / modifications."""
    items = [
        _mk_item(
            "Add new section on git-worktree edge cases",
            kind="success",
            requires_new_reference_file=True,
        ),
        _mk_item(
            "Edit case in Examples",
            kind="failure",
            section_anchor="Examples",
            requires_new_reference_file=False,
        ),
    ]
    output = render_proposals_markdown(
        items,
        target_skill_path="/fake/path/SKILL.md",
        target_skill_md_content="# Test Skill\n\n## Examples\n\nSome example text.\n",
    )
    assert "## Marked for v0.2" in output
    assert "Add new section on git-worktree edge cases" in output
    # Locate which section the v0.2 item is in.
    v02_idx = output.index("## Marked for v0.2")
    v02_section = output[v02_idx:]
    assert "Add new section on git-worktree edge cases" in v02_section
    # The non-v02 item must NOT appear in the v0.2 section.
    assert "Edit case in Examples" not in v02_section


def test_partition_separates_v02_items() -> None:
    """partition_by_v02_marker splits items into (main, v02)."""
    items = [
        _mk_item("A", requires_new_reference_file=False),
        _mk_item("B", requires_new_reference_file=True),
        _mk_item("C", requires_new_reference_file=False),
    ]
    main, v02 = partition_by_v02_marker(items)
    assert len(main) == 2
    assert len(v02) == 1
    assert v02[0]["title"] == "B"


# ---------------------------------------------------------------------------
# Test 3 — unified diff for modifications.
# ---------------------------------------------------------------------------


def test_unified_diff_block_per_modification() -> None:
    """Each modification (kind=failure) produces a fenced ```diff block with
    + / - lines."""
    items = [
        _mk_item(
            "Refine Examples — avoid bash for git",
            description="Add anti-pattern note",
            content="Use the Git tool instead of Bash for git operations.",
            kind="failure",
            section_anchor="Examples",
        ),
    ]
    target_skill_content = (
        "# Test Skill\n\n## Examples\n\nSome example text here.\n\nMore content.\n"
    )
    output = render_proposals_markdown(
        items,
        target_skill_path="/fake/path/SKILL.md",
        target_skill_md_content=target_skill_content,
    )
    assert "## Proposed modifications" in output
    # Must contain a fenced diff block.
    assert "```diff" in output
    # Must contain at least one `+ ` insertion line within the diff block.
    diff_blocks = re.findall(r"```diff\n(.*?)```", output, re.DOTALL)
    assert len(diff_blocks) >= 1, "expected at least one ```diff fenced block"
    plus_lines = [
        line for block in diff_blocks for line in block.splitlines() if line.startswith("+")
    ]
    assert len(plus_lines) >= 1, "diff block must include at least one + line"


def test_addition_uses_insert_tag() -> None:
    """kind=success items render under §Proposed additions with the
    `[insert into §<section>]` tag."""
    items = [
        _mk_item(
            "Show successful pattern X",
            kind="success",
            section_anchor="Examples",
        ),
    ]
    output = render_proposals_markdown(
        items,
        target_skill_path="/fake/path/SKILL.md",
        target_skill_md_content="# Test\n",
    )
    assert "## Proposed additions" in output
    assert "[insert into §Examples]" in output


# ---------------------------------------------------------------------------
# Test 4 — snapshot.
# ---------------------------------------------------------------------------


def test_snapshot_matches_expected_output(tmp_path: Path) -> None:
    """End-to-end: fixture_subagent_results.json → propose.py → markdown that
    matches fixture_expected_proposals.md (normalized for date + trailing ws)."""
    assert _FIXTURE_INPUT.exists(), f"missing fixture: {_FIXTURE_INPUT}"
    assert _FIXTURE_EXPECTED.exists(), f"missing snapshot: {_FIXTURE_EXPECTED}"

    out_path = tmp_path / "actual_proposals.md"
    # Use the CLI form so the test exercises the entrypoint.
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "propose",
            "--input",
            str(_FIXTURE_INPUT),
            "--target-skill",
            "/fake/skills/example/SKILL.md",
            "--output",
            str(out_path),
            "--skill-content-file",
            str(_SCRIPTS_DIR / "fixture_sample_skill.md"),
        ],
        cwd=str(_SCRIPTS_DIR),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"propose CLI failed: {result.stderr}"
    assert out_path.exists(), "propose.py must write the output file"

    actual = _normalize_markdown(out_path.read_text())
    expected = _normalize_markdown(_FIXTURE_EXPECTED.read_text())
    assert actual == expected, (
        f"snapshot mismatch.\n"
        f"--- expected ---\n{expected}\n"
        f"--- actual ---\n{actual}\n"
    )


# ---------------------------------------------------------------------------
# Misc helpers — normalization defaults.
# ---------------------------------------------------------------------------


def test_normalize_memory_item_defaults() -> None:
    """Missing optional fields get safe defaults."""
    raw = {"title": "T", "description": "D", "content": "C", "kind": "failure"}
    norm = normalize_memory_item(raw)
    assert norm["section_anchor"] == "Examples"
    assert norm["requires_new_reference_file"] is False


def test_extract_memory_items_flattens_sessions() -> None:
    """Walk session-keyed list, flatten all memory_items."""
    results = [
        {
            "session_id": "s1",
            "target_skill_path": "/x/SKILL.md",
            "memory_items": [_mk_item("A"), _mk_item("B")],
        },
        {
            "session_id": "s2",
            "target_skill_path": "/x/SKILL.md",
            "memory_items": [_mk_item("C")],
        },
    ]
    items = extract_memory_items(results)
    assert len(items) == 3
    assert {it["title"] for it in items} == {"A", "B", "C"}


def test_propose_to_apply_roundtrip(tmp_path: Path) -> None:
    """End-to-end pipeline integration: propose.py output → apply.py --approved
    → target SKILL.md updated.

    This test pins the format-contract between the two scripts that
    per-task review missed in round 1: propose.py was emitting headings
    apply.py couldn't parse + unified-diff headers apply.py rejected,
    so apply.py silently no-op'd on every real run. The fix changed
    propose.py to emit apply.py's canonical heading + plain `- ` / `+ `
    line format (see propose.py docstring + apply.py:32-69).

    Steps:
    1. Build a tiny fixture SKILL.md + matching subagent_results.json.
    2. Run propose.py main on fixture → captured proposals.md.
    3. Run apply.py main with --approved against the captured proposals.
    4. Assert SKILL.md was actually modified — addition appears in its
       target section and modification replaced the targeted lines.
    """
    # 1. Fixture SKILL.md with two sections.
    target_skill = tmp_path / "target_SKILL.md"
    target_skill.write_text(
        "# Tiny Skill\n"
        "\n"
        "## When to Use\n"
        "\n"
        "Old line one.\n"
        "Old line two.\n"
        "\n"
        "## Procedure\n"
        "\n"
        "Do the thing.\n",
        encoding="utf-8",
    )

    # 2. Subagent results JSON: 1 success (→ addition under §When to Use)
    #    and 1 failure (→ modification of §When to Use existing lines).
    subagent_results = [
        {
            "session_id": "rt-session-1",
            "target_skill_path": str(target_skill),
            "memory_items": [
                {
                    "title": "Show parallel-dispatch pattern",
                    "description": "Success: parallel dispatch worked.",
                    "content": "Dispatch with multiple Agent calls in one message.",
                    "kind": "success",
                    "section_anchor": "When to Use",
                    "requires_new_reference_file": False,
                },
                {
                    "title": "Refine existing guidance",
                    "description": "Failure: old guidance was unclear.",
                    "content": "New guidance — must read before edit.",
                    "kind": "failure",
                    "section_anchor": "When to Use",
                    "requires_new_reference_file": False,
                },
            ],
        }
    ]
    input_path = tmp_path / "subagent_results.json"
    input_path.write_text(json.dumps(subagent_results), encoding="utf-8")

    # 3. Run propose.py main → captured proposals.md.
    proposals_path = tmp_path / "proposals.md"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "propose",
            "--input",
            str(input_path),
            "--target-skill",
            str(target_skill),
            "--output",
            str(proposals_path),
            "--skill-content-file",
            str(target_skill),
        ],
        cwd=str(_SCRIPTS_DIR),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"propose CLI failed: {result.stderr}"
    assert proposals_path.exists()

    # Snapshot the before-state so we can assert apply.py actually wrote.
    before = target_skill.read_text(encoding="utf-8")

    # 4. Run apply.py with --approved against the captured proposals.
    apply_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "apply",
            "--proposal",
            str(proposals_path),
            "--target-skill",
            str(target_skill),
            "--approved",
        ],
        cwd=str(_SCRIPTS_DIR),
        capture_output=True,
        text=True,
    )
    assert apply_result.returncode == 0, (
        f"apply CLI failed: rc={apply_result.returncode} "
        f"stderr={apply_result.stderr}\n"
        f"--- proposals.md ---\n{proposals_path.read_text(encoding='utf-8')}"
    )

    # 5. Assert SKILL.md was actually modified — the critical check that
    #    failed silently in round 1 (rc=0 + no-op).
    after = target_skill.read_text(encoding="utf-8")
    assert after != before, (
        "apply.py reported success but SKILL.md is unchanged — the "
        "format contract between propose.py and apply.py is broken "
        "(round-1 root cause).\n"
        f"--- proposals.md ---\n{proposals_path.read_text(encoding='utf-8')}\n"
        f"--- SKILL.md ---\n{after}"
    )
    # Addition landed in §When to Use, before §Procedure.
    assert "Dispatch with multiple Agent calls in one message." in after
    addition_idx = after.index("Dispatch with multiple Agent calls in one message.")
    when_idx = after.index("## When to Use")
    procedure_idx = after.index("## Procedure")
    assert when_idx < addition_idx < procedure_idx, (
        "Addition must land inside §When to Use, before §Procedure."
    )
    # Modification text landed in §When to Use too.
    assert "New guidance — must read before edit." in after


def test_cli_module_form_runs(tmp_path: Path) -> None:
    """`python -m propose ...` runs without error on a tiny input."""
    inp = tmp_path / "in.json"
    inp.write_text(
        json.dumps(
            [
                {
                    "session_id": "s1",
                    "target_skill_path": "/x/SKILL.md",
                    "memory_items": [
                        {
                            "title": "Trivial",
                            "description": "d",
                            "content": "c",
                            "kind": "success",
                            "section_anchor": "Examples",
                        }
                    ],
                }
            ]
        )
    )
    skill = tmp_path / "skill.md"
    skill.write_text("# T\n\n## Examples\n\nfoo\n")
    out = tmp_path / "out.md"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "propose",
            "--input",
            str(inp),
            "--target-skill",
            "/x/SKILL.md",
            "--output",
            str(out),
            "--skill-content-file",
            str(skill),
        ],
        cwd=str(_SCRIPTS_DIR),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    assert out.exists()
