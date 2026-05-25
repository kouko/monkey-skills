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

import pytest

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


def test_anchor_mismatch_routes_to_review_bucket() -> None:
    """v0.2 Finding #4 part 2: items whose section_anchor doesn't match a
    real heading in the target SKILL.md go to §"Anchor mismatch — needs
    review", NOT into Proposed additions / modifications.

    Without this routing, propose.py silently emits additions tagged
    ``[insert into §<dead-section>]`` that apply.py would refuse at the
    DiffMismatch gate. Surfacing the gap as a distinct review bucket
    forces the operator (or v1.0 broad-scope mining) to assign a real
    anchor before approval.
    """
    skill_md = (
        "# Test Skill\n\n"
        "## When to use\n\nFoo.\n\n"
        "## Self-review\n\nBar.\n"
    )
    items = [
        _mk_item(
            "Hits real heading",
            kind="success",
            section_anchor="When to use",
        ),
        _mk_item(
            "Misses heading",
            kind="success",
            section_anchor="Definitely Not A Heading",
        ),
        _mk_item(
            "Mod against real heading",
            kind="failure",
            section_anchor="Self-review",
        ),
        _mk_item(
            "Mod against missing heading",
            kind="failure",
            section_anchor="Nope",
        ),
    ]
    output = render_proposals_markdown(
        items,
        target_skill_path="/fake/path/SKILL.md",
        target_skill_md_content=skill_md,
    )

    # New bucket must exist and contain the mismatched items.
    assert "## Anchor mismatch — needs review" in output, (
        "render must include §'Anchor mismatch — needs review' for items "
        "whose section_anchor doesn't match a real heading"
    )
    # Bound mismatch_section between its own heading and the next ## heading
    # (§Marked for v0.2 in this fixture). Slicing to end-of-string would
    # accidentally include later buckets and produce false-negative on
    # "Hits real heading" assertion if a later bucket happened to mention it.
    mismatch_idx = output.index("## Anchor mismatch — needs review")
    next_heading_idx = output.index("## Marked for v0.2", mismatch_idx)
    mismatch_section = output[mismatch_idx:next_heading_idx]
    assert "Misses heading" in mismatch_section
    assert "Mod against missing heading" in mismatch_section
    assert "Definitely Not A Heading" in mismatch_section
    assert "Nope" in mismatch_section

    # Matched items must NOT be in the mismatch bucket.
    assert "Hits real heading" not in mismatch_section
    assert "Mod against real heading" not in mismatch_section

    # Matched items must still appear in their normal bucket.
    additions_idx = output.index("## Proposed additions")
    modifications_idx = output.index("## Proposed modifications")
    additions_section = output[additions_idx:modifications_idx]
    assert "Hits real heading" in additions_section
    assert "Misses heading" not in additions_section


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
    # Target SKILL.md must carry the §Examples heading so the new
    # anchor-match partition (v0.2 Finding #4) routes the addition to
    # §Proposed additions rather than §Anchor mismatch — needs review.
    output = render_proposals_markdown(
        items,
        target_skill_path="/fake/path/SKILL.md",
        target_skill_md_content="# Test\n\n## Examples\n\nstuff.\n",
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


def test_normalize_memory_item_rejects_missing_section_anchor() -> None:
    """v0.2 Finding #4: section_anchor must be explicit, no silent default.

    v0.1 defaulted missing section_anchor to "Examples", which is dead on real
    code-toolkit SKILL.md files (none ship that heading). v0.2 makes the field
    REQUIRED at normalization time so the gap surfaces immediately instead of
    silently producing proposals against a non-existent section.
    """
    raw = {"title": "T", "description": "D", "content": "C", "kind": "failure"}
    with pytest.raises(ValueError, match="section_anchor"):
        normalize_memory_item(raw)

    raw_empty = {**raw, "section_anchor": "   "}
    with pytest.raises(ValueError, match="section_anchor"):
        normalize_memory_item(raw_empty)


def test_normalize_memory_item_defaults_for_optional_fields() -> None:
    """Optional fields (requires_new_reference_file) still get safe defaults.

    Only section_anchor was promoted to REQUIRED in v0.2; the v0.2-bucket
    routing flag stays optional (Q4: most items don't need new reference
    files).
    """
    raw = {
        "title": "T",
        "description": "D",
        "content": "C",
        "kind": "failure",
        "section_anchor": "Examples",
    }
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


def test_extract_skill_md_headings_skips_fenced_code_block_content() -> None:
    """Headings inside fenced code blocks must NOT register as valid anchors.

    Regression for v2.6.1 hotfix: prior implementation matched any line
    starting with ``#``, so a ``## fake heading`` inside a ``` ```bash ``` ``
    block would falsely appear as a valid SKILL.md anchor — allowing a
    Memory Item whose ``section_anchor`` happened to match the in-code
    text to route to anchor_ok instead of §"Anchor mismatch — needs review".
    """
    from propose import extract_skill_md_headings

    md = (
        "# Real Title\n"
        "\n"
        "## Real Heading\n"
        "\n"
        "some prose.\n"
        "\n"
        "```bash\n"
        "# this is a bash comment, not a heading\n"
        "## another fake heading\n"
        "echo hi\n"
        "```\n"
        "\n"
        "## Another Real Heading\n"
    )
    headings = extract_skill_md_headings(md)
    assert headings == {"Real Title", "Real Heading", "Another Real Heading"}, (
        f"Expected only outside-fence headings, got: {sorted(headings)}"
    )


def test_render_proposal_includes_cross_session_evidence_pending_section() -> None:
    """cluster_memory_items is wired into render_proposals_markdown:
    - items appearing in >= 2 distinct sessions are PROMOTED → existing sections
    - items appearing in only 1 session are PENDING → §Cross-session evidence pending

    Fixture:
      item_A  session_a  title="Pattern X"    anchor=Examples  kind=success
      item_B  session_b  title="Pattern X"    anchor=Examples  kind=success  → same (title,anchor) → 2 sessions → PROMOTED
      item_C  session_a  title="Unique pattern"  anchor=Examples  kind=success  → 1 session → PENDING

    Section ordering (per spec):
      ## Proposed additions
      ## Proposed modifications
      ## Anchor mismatch — needs review
      ## Cross-session evidence pending
      ## Marked for v0.2
    """
    skill_md = "# Test Skill\n\n## Examples\n\nSome text.\n"

    # Build normalized items with session_id so cluster_memory_items can count
    # distinct sessions.  _source_session mirrors session_id (extract_memory_items
    # sets both when going through the CLI path).
    def _mk_session_item(
        title: str,
        session_id: str,
        *,
        anchor: str = "Examples",
        kind: str = "success",
    ) -> dict:
        return {
            "title": title,
            "description": f"desc for {title}",
            "content": f"content for {title}",
            "kind": kind,
            "section_anchor": anchor,
            "requires_new_reference_file": False,
            "_source_session": session_id,
            "session_id": session_id,
        }

    item_a = _mk_session_item("Pattern X", "session_a")
    item_b = _mk_session_item("Pattern X", "session_b")
    item_c = _mk_session_item("Unique pattern", "session_a")

    output = render_proposals_markdown(
        [item_a, item_b, item_c],
        target_skill_path="/fake/SKILL.md",
        target_skill_md_content=skill_md,
        run_date="2026-01-01",
    )

    # --- §Cross-session evidence pending section must exist ---
    assert "## Cross-session evidence pending" in output, (
        "render_proposals_markdown must include §'Cross-session evidence pending' "
        "for items whose group has only 1 distinct session"
    )

    # Locate section boundaries for precise scoping.
    pending_idx = output.index("## Cross-session evidence pending")
    v02_idx = output.index("## Marked for v0.2", pending_idx)
    pending_section = output[pending_idx:v02_idx]

    # "Unique pattern" must appear under pending with session_a annotation.
    assert "Unique pattern" in pending_section, (
        "single-session item content must appear in §Cross-session evidence pending"
    )
    assert "session_a" in pending_section, (
        "pending section must annotate the source session_id"
    )

    # "Pattern X" must NOT appear under pending — it is promoted.
    assert "Pattern X" not in pending_section, (
        "promoted item (Pattern X, 2 sessions) must NOT appear in §Cross-session evidence pending"
    )

    # --- Promoted "Pattern X" must appear under §Proposed additions ---
    additions_idx = output.index("## Proposed additions")
    modifications_idx = output.index("## Proposed modifications")
    additions_section = output[additions_idx:modifications_idx]

    assert "Pattern X" in additions_section, (
        "promoted kind=success item must appear in §Proposed additions"
    )

    # Promoted items must carry supporting_sessions annotation.
    assert "session_a" in additions_section, (
        "promoted item must show session_a in §Proposed additions"
    )
    assert "session_b" in additions_section, (
        "promoted item must show session_b in §Proposed additions"
    )

    # --- Section ordering ---
    idx_additions = output.index("## Proposed additions")
    idx_modifications = output.index("## Proposed modifications")
    idx_anchor_mismatch = output.index("## Anchor mismatch — needs review")
    idx_pending = output.index("## Cross-session evidence pending")
    idx_v02 = output.index("## Marked for v0.2")

    assert idx_additions < idx_modifications < idx_anchor_mismatch < idx_pending < idx_v02, (
        "Section ordering must be: Proposed additions → Proposed modifications → "
        "Anchor mismatch — needs review → Cross-session evidence pending → Marked for v0.2"
    )


def test_extract_skill_md_headings_skips_indented_fenced_code_block() -> None:
    """Indented fences (fenced blocks nested inside list items) also count.

    Whole-branch review 2026-05-25 surfaced this edge: the SKILL.md
    currently has 4 indented fences (e.g. inside numbered-list bodies)
    that would not be detected by a plain ``startswith("```")``. Today
    none of them contain heading-like lines, but the silent-failure
    mode would be a false-positive anchor once one does.
    """
    from propose import extract_skill_md_headings

    md = (
        "## Real Heading\n"
        "\n"
        "1. List item with embedded code:\n"
        "\n"
        "   ```bash\n"
        "   ## fake heading inside indented fence\n"
        "   ```\n"
        "\n"
        "## Tail Real Heading\n"
    )
    headings = extract_skill_md_headings(md)
    assert headings == {"Real Heading", "Tail Real Heading"}, (
        f"Indented fence should suppress inner headings; got: {sorted(headings)}"
    )
