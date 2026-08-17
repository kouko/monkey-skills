"""Structural grep-test guarding the archive-on-close step in
finishing-a-development-branch/SKILL.md (plan Task 11).

finishing-a-development-branch/SKILL.md is a prompt artifact, not
executable code. Its correctness is the PRESENCE of the archive-on-close
step: when the branch consumed a loom-design change-folder (bound per
writing-plans' detection cascade — see
loom-code/skills/writing-plans/SKILL.md §Consuming a loom-design
change-folder) and its scenarios shipped, the orchestrator runs
`archive_change_folder.py` to move `docs/loom/<change-id>/` into
`docs/loom/archive/`, then stages that move in the close-out commit.
When no change-folder was bound, the step must say so loudly — never a
silent skip — using the exact phrase
"archive-on-close: N/A — no change-folder bound".

The step lives in Step 8's close-out sub-checks table (the five
ONCE-per-branch bullets collapsed into one table in loom arc 4b),
directly after the Living-spec index regen row; the table's lead-in
sentence carries the shared scope (orchestrator-only, once per branch —
a parallel wave would race each check's target file) exactly once for
every row.

These checks assert on load-bearing PHRASES (intent), tolerant of
wording variation, so the test guards meaning without being brittle.

Stdlib only (pathlib). Resolve SKILL.md relative to this test file.
"""

from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "finishing-a-development-branch" / "SKILL.md"
AGENTS_MD = Path(__file__).parents[2] / "AGENTS.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _archive_neighborhood(text: str) -> str:
    """The Archive-on-close table ROW plus the table's lead-in sentence.

    Scopes assertions to the archive-on-close row itself. Without this,
    generic words like "stage" / "close-out commit" also appear in the
    sibling rows, so a whole-file substring check passes even with the
    archive row's own wording missing (false-green). The bullet-era
    version of this helper was a ±600-char radius window; the row is one
    physical line, so extraction is now line-scoped. The lead-in line
    above the table carries "orchestrator-only" / "ONCE per branch" for
    every row exactly once, so it is part of the guarded text: delete the
    lead-in and the orchestrator-only test goes red."""
    idx = text.find("archive_change_folder.py")
    assert idx != -1, "archive_change_folder.py must be present"
    row_start = text.rfind("\n", 0, idx) + 1
    row = text[row_start:].splitlines()[0]

    lead_start = text.find("Close-out sub-checks")
    assert lead_start != -1, \
        'the "Close-out sub-checks" lead-in above the table must be present'
    header_start = text.find("| Check |", lead_start)
    assert header_start != -1 and header_start < idx, \
        "table header must sit between the lead-in and the archive row"
    return text[lead_start:header_start] + "\n" + row


def test_archive_step_names_the_script():
    """The archive-on-close step must name archive_change_folder.py so a
    reader knows exactly which script runs."""
    text = _text()
    assert "archive_change_folder.py" in text, \
        "must name the archive_change_folder.py script"


def test_archive_step_gated_on_change_folder_and_shipped_scenarios():
    """The step only fires when the branch consumed a bound change-folder
    AND its scenarios shipped — not unconditionally."""
    text = _text()
    low = text.lower()

    assert "change-folder" in low, \
        "must reference the change-folder concept"
    assert "bound" in low, \
        "must reference the writing-plans binding (bound per the detection cascade)"
    assert "shipped" in low, \
        "must gate on the change-folder's scenarios having shipped"


def test_archive_step_recovers_bound_ness_from_plan_join_keys():
    """Round-2 fix (quality review Finding 1): the step must state HOW the
    finishing-time orchestrator recovers "bound per writing-plans'
    detection cascade" — binding happened in an earlier dispatch, possibly
    another session — by deriving it from the plan document's own
    change-folder join keys, never by guessing from content similarity."""
    text = _text()
    low = text.lower()

    assert "docs/loom/plans/" in text, \
        "must name the plan document path to grep for join keys"
    assert "join key" in low, \
        "must name the join-key mechanism used to recover bound-ness"
    assert "requirement:" in low and "scenario:" in low, \
        "must reference the join-key pattern (Requirement: / Scenario:)"
    assert "never guess" in low, \
        "must forbid guessing a change-id from content similarity"


def test_archive_step_na_loud_when_unbound():
    """When no change-folder was bound, the step states the exact N/A
    line — never a silent skip."""
    text = _text()
    assert "archive-on-close: N/A — no change-folder bound" in text, \
        'must state the exact N/A line: "archive-on-close: N/A — no change-folder bound"'


def test_archive_step_stages_the_move_in_close_out_commit():
    """The resulting move (docs/loom/<change-id>/ -> docs/loom/archive/...)
    must be staged so it lands in the close-out commit, mirroring the
    Living-spec index regen row's stage-it-here instruction.

    Scoped to the archive row itself: "stage" and "close-out commit"
    both also appear in the sibling rows, so an unscoped whole-file
    check would pass even with the archive row's own staging
    instruction absent."""
    text = _text()
    window = _archive_neighborhood(text).lower()

    assert "stage" in window, \
        "must instruct staging the archive move (near the archive_change_folder.py mention)"
    assert "close-out commit" in window, \
        "must say the staged move lands in the close-out commit (near the archive_change_folder.py mention)"


def test_archive_step_is_orchestrator_only_once_per_branch():
    """Orchestrator-only, run once per branch — never per-implementer or
    per-wave (would race the same folder under parallel SDD). Since the
    arc-4b collapse the table's lead-in sentence carries this scope once
    for every row, so the guarded text is the lead-in plus the archive
    row: delete the lead-in and this test goes red."""
    text = _text()
    window = _archive_neighborhood(text).lower()

    assert "orchestrator-only" in window, \
        "must mark the step orchestrator-only (near the archive_change_folder.py mention)"
    assert "once per branch" in window, \
        "must mark the step as running once per branch (near the archive_change_folder.py mention)"


def test_archive_step_placed_near_living_spec_index_row():
    """The step belongs in the Step 8 close-out sub-checks table, near
    the Living-spec index regen row — not scattered elsewhere in the
    file. Row adjacency in the table satisfies the proximity pin."""
    text = _text()
    living_spec_idx = text.find("Living-spec index regen")
    archive_idx = text.find("archive_change_folder.py")

    assert living_spec_idx != -1, "Living-spec index regen row must still be present"
    assert archive_idx != -1, "archive_change_folder.py must be present"
    # Both rows should live within the same ~2000-char Step 8 table.
    assert abs(archive_idx - living_spec_idx) < 2000, \
        "archive-on-close row must sit near the Living-spec index regen row (Step 8 close-out sub-checks table)"


def test_agents_md_declares_archive_script():
    """Command-surface accretion obligation (Task 11 amendment): AGENTS.md's
    managed command-surface block must declare archive_change_folder.py so
    the new runnable verb has a declared entry point."""
    assert AGENTS_MD.is_file(), f"AGENTS.md is absent at {AGENTS_MD}"
    text = AGENTS_MD.read_text(encoding="utf-8")
    start = text.index("BEGIN command-surface (managed)")
    end = text.index("END command-surface (managed)")
    managed_block = text[start:end]
    assert "archive_change_folder.py" in managed_block, \
        "AGENTS.md managed command-surface block must declare archive_change_folder.py"
