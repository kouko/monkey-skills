"""Structural grep-test guarding the archive-on-close step in
finishing-a-development-branch/SKILL.md (plan Task 11).

finishing-a-development-branch/SKILL.md is a prompt artifact, not
executable code. Its correctness is the PRESENCE of the archive-on-close
step: when the branch consumed a loom-spec change-folder (bound per
writing-plans' detection cascade — see
loom-code/skills/writing-plans/SKILL.md §Consuming a loom-spec
change-folder) and its scenarios shipped, the orchestrator runs
`archive_change_folder.py` to move `docs/loom/<change-id>/` into
`docs/loom/archive/`, then stages that move in the close-out commit.
When no change-folder was bound, the step must say so loudly — never a
silent skip — using the exact phrase
"archive-on-close: N/A — no change-folder bound".

The step lives in the git-hygiene area (Step 8), alongside the
living-spec index regen bullet: same shape (orchestrator-only, once per
branch, not per-implementer/per-wave — a per-implementer archive under
parallel SDD would race the same folder).

These checks assert on load-bearing PHRASES (intent), tolerant of
wording variation, so the test guards meaning without being brittle.

Stdlib only (pathlib). Resolve SKILL.md relative to this test file.
"""

from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "finishing-a-development-branch" / "SKILL.md"
AGENTS_MD = Path(__file__).parents[2] / "AGENTS.md"

# How far (in characters) around the archive_change_folder.py mention to look
# for words that also occur, verbatim, in neighboring Step 8 bullets (the
# living-spec index bullet above, the Memory-timing bullet below). A window
# this size covers the archive bullet's own text without spilling into either
# neighbor — see test_archive_step_placed_near_living_spec_index_bullet for
# the sibling technique this mirrors.
_NEIGHBORHOOD_RADIUS = 600


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _archive_neighborhood(text: str, radius: int = _NEIGHBORHOOD_RADIUS) -> str:
    """Window of text centered on the archive_change_folder.py mention.

    Scopes assertions to the archive-on-close bullet itself. Without this,
    generic words like "stage" / "orchestrator-only" / "once per branch"
    also appear in the living-spec-index and memory-timing bullets, so a
    whole-file substring check passes even with the archive bullet's own
    wording missing (false-green)."""
    idx = text.find("archive_change_folder.py")
    assert idx != -1, "archive_change_folder.py must be present"
    start = max(0, idx - radius)
    end = min(len(text), idx + radius)
    return text[start:end]


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
    living-spec index regen bullet's stage-it-here instruction.

    Scoped to the archive bullet's own neighborhood: "stage" and
    "close-out commit" both also appear in the living-spec-index and
    memory-timing bullets, so an unscoped whole-file check would pass
    even with the archive bullet's own staging instruction absent."""
    text = _text()
    window = _archive_neighborhood(text).lower()

    assert "stage" in window, \
        "must instruct staging the archive move (near the archive_change_folder.py mention)"
    assert "close-out commit" in window, \
        "must say the staged move lands in the close-out commit (near the archive_change_folder.py mention)"


def test_archive_step_is_orchestrator_only_once_per_branch():
    """Same shape as the living-spec index regen bullet immediately above
    it: orchestrator-only, run once per branch — never per-implementer or
    per-wave (would race the same folder under parallel SDD).

    Scoped to the archive bullet's own neighborhood: "orchestrator-only"
    and "once per branch" both also appear in the living-spec-index and
    memory-timing bullets, so an unscoped whole-file check would pass
    even with the archive bullet's own orchestrator-only/once-per-branch
    marking absent."""
    text = _text()
    window = _archive_neighborhood(text).lower()

    assert "orchestrator-only" in window, \
        "must mark the step orchestrator-only (near the archive_change_folder.py mention)"
    assert "once per branch" in window, \
        "must mark the step as running once per branch (near the archive_change_folder.py mention)"


def test_archive_step_placed_near_living_spec_index_bullet():
    """The step belongs in the Step 8 git-hygiene area, near the
    living-spec index regen bullet — not scattered elsewhere in the file."""
    text = _text()
    living_spec_idx = text.find("Living-spec index regen")
    archive_idx = text.find("archive_change_folder.py")

    assert living_spec_idx != -1, "living-spec index regen bullet must still be present"
    assert archive_idx != -1, "archive_change_folder.py must be present"
    # Both bullets should live within the same ~2000-char Step 8 neighborhood.
    assert abs(archive_idx - living_spec_idx) < 2000, \
        "archive-on-close step must sit near the living-spec index regen bullet (Step 8 git-hygiene area)"


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
